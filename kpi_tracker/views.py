from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import BreastKPI, KPIActivityLog
from .forms import BreastKPIForm
from django.db.models import Avg, Max, Min, Count
from django.db.models.functions import TruncMonth
import pandas as pd
from datetime import datetime, timedelta
import time
from .utils import get_azure_db_connection, retrieve_mrn_data, calculate_age, en_mrn
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .kpi_definitions import BREAST_KPI_DEFINITIONS
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db import models
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from .auth import get_auth_url, get_token_from_code, get_user_info
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.models import Group
from urllib.parse import quote
import os
from django.db import connection
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.utils import timezone
import csv
import msal
import uuid

User = get_user_model()

def breast_kpi_dashboard(request):
    # Start with all entries
    entries = BreastKPI.objects.filter(Pending=False)
    
    # Let's modify to show both totals
    total_completed = entries.count()
    total_pending = BreastKPI.objects.filter(Pending=True).count()
    total_all = total_completed + total_pending
    
    # Calculate new cases trend
    new_cases_trend = list(entries.filter(Screening_date__isnull=False)
        .annotate(month=TruncMonth('Screening_date'))
        .values('month')
        .annotate(count=Count('MRN'))
        .order_by('month'))
    
    # Calculate demographics with proper handling of nationality
    demographics = {
        'nationality': list(entries.values('Nationality')
            .annotate(count=Count('MRN'))
            .filter(Nationality__isnull=False)
            .exclude(Nationality='')  # Exclude empty strings
            .order_by('-count')),  # Order by count descending
        'gender': list(entries.values('Gender')
            .annotate(count=Count('MRN'))
            .filter(Gender__isnull=False)),
        'age_groups': []
    }
    
    # Transform nationality data to match expected format
    demographics['nationality'] = [
        {
            'nationality': item['Nationality'],
            'count': item['count']
        }
        for item in demographics['nationality']
    ]

    
    # Calculate age groups
    age_ranges = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 200)]
    age_groups = []

    # First calculate totals for each age group
    for start, end in age_ranges:
        total_male = entries.filter(
            Age__gte=start, 
            Age__lte=end, 
            Gender='Male'
        ).count()
        
        total_female = entries.filter(
            Age__gte=start, 
            Age__lte=end, 
            Gender='Female'
        ).count()
        
        if total_male > 0 or total_female > 0:
            age_groups.append({
                'age_group': f'{start}-{end}',
                'male_count': total_male,
                'female_count': total_female
            })

    # Then calculate nationality-specific counts
    nationality_age_groups = []
    nationalities = entries.values_list('Nationality', flat=True).distinct()

    for nationality in nationalities:
        for start, end in age_ranges:
            nationality_entries = entries.filter(Nationality=nationality)
            male_count = nationality_entries.filter(
                Age__gte=start, 
                Age__lte=end, 
                Gender='Male'
            ).count()
            female_count = nationality_entries.filter(
                Age__gte=start, 
                Age__lte=end, 
                Gender='Female'
            ).count()
            
            if male_count > 0 or female_count > 0:
                nationality_age_groups.append({
                    'age_group': f'{start}-{end}',
                    'nationality': nationality,
                    'male_count': male_count,
                    'female_count': female_count
                })

    # Store both total and nationality-specific data
    demographics['age_groups'] = {
        'total': age_groups,
        'by_nationality': nationality_age_groups
    }
    
    # Calculate Treatment Start Time KPI
    treatment_entries = entries.exclude(Treatment_NotFitForThisKPI=True).filter(
        Insurance_date__isnull=False,
        Treatment_date__isnull=False
    )
    
    # Calculate delay distribution
    delay_distribution = calculate_delay_distribution(treatment_entries)
    
    # Calculate delay reasons
    delay_reasons = calculate_delay_reasons(treatment_entries)
    
    # Calculate average time and KPI metrics
    avg_time = treatment_entries.annotate(
        days_to_treatment=models.ExpressionWrapper(
            models.F('Treatment_date') - models.F('Insurance_date'),
            output_field=models.DurationField()
        )
    ).aggregate(
        avg_days=models.Avg('days_to_treatment')
    )['avg_days']
    
    avg_days = avg_time.days if avg_time else 0
    
    within_target = treatment_entries.filter(
        Treatment_date__lte=models.F('Insurance_date') + timedelta(days=31)
    ).count()
    
    total_cases = treatment_entries.count()
    
    treatment_kpi = {
        'total': total_cases,
        'within_target': within_target,
        'percentage': (within_target / total_cases * 100) if total_cases > 0 else 0,
        'avg_days': avg_days
    }
    

    # Get unique doctors for each category
    doctors = {
        'oncologists': list(entries.values('Oncologist_name')
            .exclude(Oncologist_name__isnull=True)
            .exclude(Oncologist_name='')
            .distinct()
            .order_by('Oncologist_name')),
        'surgeons': list(entries.values('Surgeon_name')
            .exclude(Surgeon_name__isnull=True)
            .exclude(Surgeon_name='')
            .distinct()
            .order_by('Surgeon_name')),
        'radiotherapists': list(entries.values('Radiotherapist_name')
            .exclude(Radiotherapist_name__isnull=True)
            .exclude(Radiotherapist_name='')
            .distinct()
            .order_by('Radiotherapist_name'))
    }

    context = {
        'new_cases_trend': json.dumps(new_cases_trend, cls=DjangoJSONEncoder),
        'demographics': {
            'nationality': demographics['nationality'],
            'gender': json.dumps(demographics['gender'], cls=DjangoJSONEncoder),
            'age_groups': json.dumps(demographics['age_groups'], cls=DjangoJSONEncoder),
        },
        'delay_distribution': json.dumps(delay_distribution, cls=DjangoJSONEncoder),
        'delay_reasons': delay_reasons,
        'doctors': {
            'oncologists': doctors['oncologists'],
            'surgeons': doctors['surgeons'],
            'radiotherapists': doctors['radiotherapists']
        },
        'total_patients': total_completed,
        'total_pending': total_pending,
        'total_all': total_all,
        'treatment_kpi': treatment_kpi,
    }
    
    return render(request, 'kpi_tracker/breast/dashboard.html', context)

def breast_kpi_form(request, mrn=None):
    instance = None
    search_mrn = request.GET.get('search_mrn')
    search_result = None
    activity_log = []
    
    if mrn:
        instance = get_object_or_404(BreastKPI, MRN=mrn)
    elif search_mrn:
        try:
            instance = BreastKPI.objects.get(MRN=search_mrn)
            return redirect('kpi_tracker:breast_form', mrn=search_mrn)
        except BreastKPI.DoesNotExist:
            search_result = {
                'type': 'info',
                'message': f'No record found for MRN: {search_mrn}. You can create a new entry.'
            }
    
    # Initialize form for both GET and POST
    if request.method == 'POST':
        form = BreastKPIForm(request.POST, instance=instance, user=request.user if request.user.is_authenticated else None)
        if form.is_valid():
            try:
                # Get the pending status directly from the checkbox
                pending_status = request.POST.get('Pending') == 'on'
                
                # Save the form with the correct pending status
                kpi_entry = form.save(commit=False)
                kpi_entry.Pending = pending_status
                kpi_entry.save()
                
                # Create activity log with user info check
                user_name = "Anonymous"
                user_email = ""
                user_id = None
                
                if request.user.is_authenticated:
                    user_name = request.user.get_full_name() or request.user.username
                    user_email = request.user.email
                    user_id = request.user.id
                
                KPIActivityLog.objects.create(
                    log_id=int(time.time() * 1000),
                    SourcePage='Breast',
                    UserName=user_name,
                    UserEmail=user_email,
                    UserID=user_id,
                    MRN=kpi_entry.MRN,
                    ts=datetime.now(),
                    Type="Update" if instance and instance.MRN else "New",
                    Pending_Status=1 if pending_status else 0
                )
                
                messages.success(request, 'KPI entry saved successfully!', extra_tags='kpi_tracker')
                return redirect('kpi_tracker:breast_list')
            except Exception as e:
                print("Error saving entry:", str(e))
                messages.error(request, f'Error saving KPI entry: {str(e)}')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = BreastKPIForm(instance=instance, user=request.user if request.user.is_authenticated else None)
    
    # Get activity log for this MRN if it exists
    if instance and instance.MRN:
        activity_log = KPIActivityLog.objects.filter(
            MRN=instance.MRN,
            SourcePage='Breast'
        ).order_by('-ts')
    
    context = {
        'form': form,
        'instance': instance,
        'search_mrn': search_mrn,
        'activity_log': activity_log,
        'search_result': search_result,
        'surgery_kpi': BREAST_KPI_DEFINITIONS['surgery'],
        'radiotherapy_kpi': BREAST_KPI_DEFINITIONS['radiotherapy'],
        'biopsy_kpi': BREAST_KPI_DEFINITIONS['biopsy'],
    }
    return render(request, 'kpi_tracker/breast/form.html', context)

def breast_kpi_list(request):
    pending_entries = BreastKPI.objects.filter(Pending=True).order_by('-entry_ts')
    completed_entries = BreastKPI.objects.filter(Pending=False).order_by('-entry_ts')
    
    # Calculate totals
    seven_days_ago = timezone.now() - timedelta(days=7)
    totals = {
        'completed': completed_entries.count(),
        'pending': pending_entries.count(),
        'new_entries': BreastKPI.objects.filter(entry_ts__gte=seven_days_ago).count(),
        'total': BreastKPI.objects.count()
    }
    
    # Calculate KPIs for completed entries
    for entry in completed_entries:
        if not entry.Surgery_NotFitForThisKPI and entry.Neoadjuvant_ctx_date and entry.Surgery_date:
            entry.surgery_status = (entry.Surgery_date - entry.Neoadjuvant_ctx_date) <= timedelta(weeks=8)
        else:
            entry.surgery_status = None
        
        if not entry.Radio_NotFitForThisKPI and entry.surgery_last_dose_adjuvant_chemotherapy_date and entry.Radio_date:
            entry.radio_status = (entry.Radio_date - entry.surgery_last_dose_adjuvant_chemotherapy_date) <= timedelta(weeks=8)
        else:
            entry.radio_status = None
    
    # Handle CSV download
    if request.GET.get('download') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="breast_kpi_data.csv"'
        
        writer = csv.writer(response)
        # Write headers
        fields = [field.name for field in BreastKPI._meta.fields]
        writer.writerow(fields)
        
        # Write data for both pending and completed entries
        for entry in list(pending_entries) + list(completed_entries):
            writer.writerow([getattr(entry, field) for field in fields])
        
        return response
    
    return render(request, 'kpi_tracker/breast/list.html', {
        'pending_entries': pending_entries,
        'completed_entries': completed_entries,
        'kpi_definitions': BREAST_KPI_DEFINITIONS,
        'totals': totals
    })

def breast_kpi_analytics(request):
    # Get completed entries
    completed_entries = BreastKPI.objects.filter(Pending=False)
    
    # Calculate KPIs
    treatment_times = []
    surgery_times = []
    radio_times = []
    
    for entry in completed_entries:
        if entry.calculate_treatment_status() is not None:
            treatment_times.append((entry.Treatment_date - entry.Insurance_date).days)
        if entry.calculate_surgery_status() is not None:
            surgery_times.append((entry.Surgery_date - entry.Neoadjuvant_ctx_date).days)
        if entry.calculate_radio_status() is not None:
            radio_times.append((entry.Radio_date - entry.surgery_last_dose_adjuvant_chemotherapy_date).days)
    
    analytics = {
        'treatment_avg': sum(treatment_times) / len(treatment_times) if treatment_times else 0,
        'surgery_avg': sum(surgery_times) / len(surgery_times) if surgery_times else 0,
        'radio_avg': sum(radio_times) / len(radio_times) if radio_times else 0,
        'total_cases': completed_entries.count(),
        'pending_cases': BreastKPI.objects.filter(Pending=True).count(),
    }
    
    return render(request, 'kpi_tracker/breast/analytics.html', {'analytics': analytics})

def breast_kpi_followup(request):
    from datetime import date, datetime, timedelta
    today = date.today()
    
    # Get filter values
    selected_cnc = request.GET.get('cnc_filter')
    selected_status = request.GET.get('status_filter')
    
    # Get all entries with upcoming or overdue follow-ups
    followups = BreastKPI.objects.filter(
        Next_Follow_up_Date__isnull=False
    )
    
    # Apply CNC filter first if selected
    if selected_cnc:
        followups = followups.filter(CNC_name=selected_cnc)
    
    # Calculate totals after applying CNC filter
    totals = {
        'overdue': followups.filter(Next_Follow_up_Date__lt=today).count(),
        'upcoming_day': followups.filter(
            Next_Follow_up_Date__gte=today,
            Next_Follow_up_Date__lte=today + timedelta(days=1)
        ).count(),
        'upcoming_month': followups.filter(
            Next_Follow_up_Date__gte=today,
            Next_Follow_up_Date__lte=today + timedelta(days=30)
        ).count(),
        'total': followups.count()
    }
    
    # Apply status filter if selected
    if selected_status:
        if selected_status == 'overdue':
            followups = followups.filter(Next_Follow_up_Date__lt=today)
        elif selected_status == 'upcoming_month':
            followups = followups.filter(
                Next_Follow_up_Date__gte=today,
                Next_Follow_up_Date__lte=today + timedelta(days=30)
            )
        elif selected_status == 'upcoming_day':
            followups = followups.filter(
                Next_Follow_up_Date__gte=today,
                Next_Follow_up_Date__lte=today + timedelta(days=1)
            )
    
    # Order by Next_Follow_up_Date
    followups = followups.order_by('Next_Follow_up_Date')
    
    # Get unique CNC names for the filter dropdown
    cnc_names = BreastKPI.objects.exclude(
        CNC_name__isnull=True
    ).exclude(
        CNC_name=''
    ).values('CNC_name').distinct().order_by('CNC_name')
    
    # Add status flags for each followup
    for followup in followups:
        followup.is_overdue = followup.Next_Follow_up_Date < today
        followup.is_upcoming_day = (
            followup.Next_Follow_up_Date >= today and 
            followup.Next_Follow_up_Date <= today + timedelta(days=1)
        )
        followup.is_upcoming_month = (
            followup.Next_Follow_up_Date >= today and 
            followup.Next_Follow_up_Date <= today + timedelta(days=30)
        )
    
    # Create filter description
    filter_description = []
    if selected_cnc:
        filter_description.append(f"CNC: {selected_cnc}")
    if selected_status:
        status_descriptions = {
            'overdue': 'Overdue',
            'upcoming_month': 'Next 30 Days',
            'upcoming_day': 'Next 24 Hours'
        }
        filter_description.append(status_descriptions.get(selected_status))
    filter_description = ' | '.join(filter_description)
    
    # Return the rendered template with the context
    return render(request, 'kpi_tracker/breast/followup.html', {
        'followups': followups,
        'cnc_names': cnc_names,
        'selected_cnc': selected_cnc,
        'selected_status': selected_status,
        'filter_description': filter_description,
        'totals': totals
    })

def calculate_delay_distribution(treatment_entries):
    delays = []
    for entry in treatment_entries:
        if entry.Insurance_date and entry.Treatment_date:
            delay = (entry.Treatment_date - entry.Insurance_date).days
            delays.append(delay)
    
    # Create bins for the histogram
    bins = {
        '0-15': 0,
        '16-31': 0,
        '32-45': 0,
        '46-60': 0,
        '61-90': 0,
        '90+': 0
    }
    
    for delay in delays:
        if delay <= 15:
            bins['0-15'] += 1
        elif delay <= 31:
            bins['16-31'] += 1
        elif delay <= 45:
            bins['32-45'] += 1
        elif delay <= 60:
            bins['46-60'] += 1
        elif delay <= 90:
            bins['61-90'] += 1
        else:
            bins['90+'] += 1
    
    return bins

def calculate_delay_reasons(treatment_entries):

    # Count reasons for delay, excluding empty and null values
    reasons = (treatment_entries
        .exclude(Reason_for_the_delay__isnull=True)
        .exclude(Reason_for_the_delay='')
        .exclude(Reason_for_the_delay__exact=' ')  # Also exclude single space
        .values('Reason_for_the_delay')
        .annotate(count=Count('MRN'))
        .order_by('-count'))
    
    total = reasons.count()  # Changed from treatment_entries.count()
    
   
    
    # Calculate percentages
    reasons_data = [
        {
            'reason': r['Reason_for_the_delay'],
            'count': r['count'],
            'percentage': (r['count'] / total * 100) if total > 0 else 0
        }
        for r in reasons
    ]
    
    return reasons_data

def login_view(request):
    # Simplified login view for development
    if settings.DEBUG:
        try:
            # Get or create superuser using Django ORM
            superuser, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True
                }
            )
            
            # Log the user in
            login(request, superuser)
            
            # Redirect to the requested page or default
            next_url = request.GET.get('next', 'kpi_tracker:breast_form')
            return redirect(next_url)
            
        except Exception as e:
            print(f"Development login error: {str(e)}")
            messages.error(request, f"Development login failed: {str(e)}")
    
    # If we get here, something went wrong
    context = {
        'debug': settings.DEBUG,
        'user_authenticated': request.user.is_authenticated,
        'session_next': request.session.get('next'),
        'is_azure_environment': False
    }
    return render(request, 'registration/login.html', context)

def auth_callback(request):
    code = request.GET.get('code')
    if code:
        try:
            # Get token using the code
            token = get_token_from_code(code)
            if not token or 'access_token' not in token:
                print("Token error:", token)  # Debug print
                messages.error(request, "Failed to get access token.")
                return redirect('kpi_tracker:login')

            # Get user info from Azure AD
            user_info = get_user_info(token)
            if not user_info:
                print("User info error:", user_info)  # Debug print
                messages.error(request, "Failed to get user information.")
                return redirect('kpi_tracker:login')

            print("User info received:", user_info)  # Debug print
            
            # Extract Azure AD ID and other user info
            azure_id = user_info.get('id')  # Changed from 'oid' to 'id'
            email = user_info.get('mail') or user_info.get('userPrincipalName')  # Try both mail fields
            first_name = user_info.get('givenName')
            last_name = user_info.get('surname')
            
            if not email:
                print("No email found in user info")  # Debug print
                messages.error(request, "No email address found in user profile.")
                return redirect('kpi_tracker:login')

            username = email.split('@')[0]  # Create username from email
            
            try:
                # Try to get existing user
                user = User.objects.get(azure_id=azure_id)
                
                # Update user info if needed
                user.email = email
                user.first_name = first_name or ''
                user.last_name = last_name or ''
                user.username = username
                user.save()
                
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name or '',
                    last_name=last_name or '',
                    azure_id=azure_id,
                    is_active=True
                )
            
            # Log the user in
            login(request, user)
            
            # Get the next URL from session if it exists
            next_url = request.session.get('next', 'kpi_tracker:breast_form')
            
            # Redirect to the next URL or default
            return redirect(next_url)
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")  # Debug print
            print(f"Exception type: {type(e)}")  # Debug print
            print(f"Exception args: {e.args}")  # Debug print
            messages.error(request, f"Authentication failed: {str(e)}")
            return redirect('kpi_tracker:login')
    
    messages.error(request, "Authentication failed. No code received.")
    return redirect('kpi_tracker:login')

def breast_kpi_dashboard_filter(request):
    # Start with all entries
    entries = BreastKPI.objects.filter(Pending=False)
    
    # Apply filters with proper date handling
    if request.GET.get('startDate'):
        try:
            start_date = datetime.strptime(request.GET['startDate'], '%Y-%m-%d')
            entries = entries.filter(Screening_date__gte=start_date)
            print(f"Filtering by start date: {start_date}, entries: {entries.count()}")
        except ValueError as e:
            print(f"Invalid start date format: {request.GET['startDate']}, error: {e}")
    
    if request.GET.get('endDate'):
        try:
            end_date = datetime.strptime(request.GET['endDate'], '%Y-%m-%d')
            # Add one day to include the end date fully
            end_date = end_date + timedelta(days=1)
            entries = entries.filter(Screening_date__lt=end_date)
            print(f"Filtering by end date: {end_date}, entries: {entries.count()}")
        except ValueError as e:
            print(f"Invalid end date format: {request.GET['endDate']}, error: {e}")
    
    # Rest of the filters...
    if request.GET.get('gender'):
        entries = entries.filter(Gender=request.GET['gender'])
    
    if request.GET.get('nationality'):
        entries = entries.filter(Nationality=request.GET['nationality'])
    
    if request.GET.get('oncologist'):
        entries = entries.filter(Oncologist_name=request.GET['oncologist'])
    
    if request.GET.get('surgeon'):
        entries = entries.filter(Surgeon_name=request.GET['surgeon'])
    
    if request.GET.get('radiotherapist'):
        entries = entries.filter(Radiotherapist_name=request.GET['radiotherapist'])

    # Calculate metrics with filtered entries...
    new_cases_trend = list(entries.filter(Screening_date__isnull=False)
        .annotate(month=TruncMonth('Screening_date'))
        .values('month')
        .annotate(count=Count('MRN'))
        .order_by('month'))
    
    demographics = calculate_demographics(entries)
    delay_distribution = calculate_delay_distribution(entries)
    delay_reasons = calculate_delay_reasons(entries)
    treatment_kpi = calculate_treatment_kpi(entries)

    response_data = {
        'new_cases_trend': new_cases_trend,
        'demographics': {
            'nationality': demographics['nationality'],
            'gender': demographics['gender'],
            'age_groups': demographics['age_groups']
        },
        'delay_distribution': delay_distribution,
        'delay_reasons': delay_reasons,
        'total_patients': entries.count(),
        'treatment_kpi': treatment_kpi
    }

    # Ensure proper JSON serialization
    return JsonResponse(
        response_data,
        encoder=DjangoJSONEncoder,
        safe=False
    )

# Helper functions
def calculate_demographics(entries):
    """Calculate demographics for the filtered entries"""
    demographics = {
        'nationality': list(entries.values('Nationality')
            .annotate(count=Count('MRN'))
            .filter(Nationality__isnull=False)
            .exclude(Nationality='')
            .order_by('-count')),
        'gender': list(entries.values('Gender')
            .annotate(count=Count('MRN'))
            .filter(Gender__isnull=False)),
        'age_groups': {}
    }
    
    # Transform nationality data
    demographics['nationality'] = [
        {
            'nationality': item['Nationality'],
            'count': item['count']
        }
        for item in demographics['nationality']
    ]

    # Calculate age groups
    age_ranges = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 200)]
    age_groups = []

    # Calculate totals for each age group
    for start, end in age_ranges:
        total_male = entries.filter(
            Age__gte=start, 
            Age__lte=end, 
            Gender='Male'
        ).count()
        
        total_female = entries.filter(
            Age__gte=start, 
            Age__lte=end, 
            Gender='Female'
        ).count()
        
        if total_male > 0 or total_female > 0:
            age_groups.append({
                'age_group': f'{start}-{end}',
                'male_count': total_male,
                'female_count': total_female
            })

    # Calculate nationality-specific counts
    nationality_age_groups = []
    nationalities = entries.values_list('Nationality', flat=True).distinct()

    for nationality in nationalities:
        for start, end in age_ranges:
            nationality_entries = entries.filter(Nationality=nationality)
            male_count = nationality_entries.filter(
                Age__gte=start, 
                Age__lte=end, 
                Gender='Male'
            ).count()
            female_count = nationality_entries.filter(
                Age__gte=start, 
                Age__lte=end, 
                Gender='Female'
            ).count()
            
            if male_count > 0 or female_count > 0:
                nationality_age_groups.append({
                    'age_group': f'{start}-{end}',
                    'nationality': nationality,
                    'male_count': male_count,
                    'female_count': female_count
                })

    demographics['age_groups'] = {
        'total': age_groups,
        'by_nationality': nationality_age_groups
    }

    return demographics

def calculate_treatment_kpi(entries):
    """Calculate treatment KPI metrics for the filtered entries"""
    treatment_entries = entries.exclude(Treatment_NotFitForThisKPI=True).filter(
        Insurance_date__isnull=False,
        Treatment_date__isnull=False
    )
    
    # Calculate average time
    avg_time = treatment_entries.annotate(
        days_to_treatment=models.ExpressionWrapper(
            models.F('Treatment_date') - models.F('Insurance_date'),
            output_field=models.DurationField()
        )
    ).aggregate(
        avg_days=models.Avg('days_to_treatment')
    )['avg_days']
    
    avg_days = avg_time.days if avg_time else 0
    
    # Calculate within target
    within_target = treatment_entries.filter(
        Treatment_date__lte=models.F('Insurance_date') + timedelta(days=31)
    ).count()
    
    total_cases = treatment_entries.count()
    
    return {
        'total': total_cases,
        'within_target': within_target,
        'percentage': (within_target / total_cases * 100) if total_cases > 0 else 0,
        'avg_days': avg_days
    }

def kpi_home(request):
    """
    View function for the KPI Disease Management home page.
    """
    return render(request, 'kpi_tracker/home.html')

def login(request):
    # Generate and store state and nonce for security
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    request.session['state'] = state
    request.session['nonce'] = nonce
    
    # Configure MSAL client
    msal_app = msal.ConfidentialClientApplication(
        settings.AZURE_AD_AUTH['CLIENT_ID'],
        authority=settings.AZURE_AD_AUTH['AUTHORITY'],
        client_credential=settings.AZURE_AD_AUTH['CLIENT_SECRET'],
    )
    
    # Get the authorization request URL
    auth_url = msal_app.get_authorization_request_url(
        scopes=settings.AZURE_AD_AUTH['SCOPE'],
        state=state,
        nonce=nonce,
        redirect_uri=settings.AZURE_AD_AUTH['REDIRECT_URI'],
        response_type=settings.AZURE_AD_AUTH['RESPONSE_TYPE'],
        response_mode=settings.AZURE_AD_AUTH['RESPONSE_MODE']
    )
    
    return redirect(auth_url)

def oauth2_callback(request):
    if request.GET.get('state') != request.session.get('state'):
        return HttpResponseForbidden()
    
    if 'error' in request.GET:
        return HttpResponseBadRequest(request.GET['error'])
    
    try:
        code = request.GET.get('code')
        user = authenticate(request, code=code)
        if user is not None:
            login(request, user)
            # Redirect to the next URL if available, otherwise to home
            next_url = request.session.get('next', '/')
            return redirect(next_url)
    except Exception as e:
        return HttpResponseServerError(str(e))
    
    return HttpResponseRedirect('/')