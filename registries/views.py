from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F, ExpressionWrapper, DurationField, IntegerField, Count, Value, BooleanField, Case, When
from django.db.models.functions import TruncMonth, Now, Abs
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta, date
import time
from .models import BMTRegistry, BMTActivityLog
from .forms import BMTRegistryForm, BMTSearchForm
import csv
from django.template.loader import get_template
from django.db import connection

def bmt_home(request):
    # Add template debugging code here
    try:
        template = get_template('registries/bmt/home.html')
        print(f"Template found at: {template.origin.name}")
    except Exception as e:
        print(f"Template error: {e}")

    today = timezone.now().date()
    week_from_now = today + timedelta(days=7)
    
    context = {
        'total_registries': BMTRegistry.objects.count(),
        'active_cases': BMTRegistry.objects.filter(death_date__isnull=True).count(),
        'due_followups': BMTRegistry.objects.filter(
            death_date__isnull=True,
            next_followup_date__lte=week_from_now
        ).count(),
        'this_year': BMTRegistry.objects.filter(
            transplant_date__year=today.year
        ).count(),
        'recent_activity': BMTActivityLog.objects.all()[:10]  # Last 10 activities
    }
    return render(request, 'registries/bmt/home.html', context)

def bmt_form(request, mrn=None, transplant_number=None):
    instance = None
    search_result = None
    
    # Get search parameters from either URL params or query params
    search_mrn = mrn or request.GET.get('mrn')
    search_transplant = transplant_number or request.GET.get('transplant_number')
    
    # Handle search using direct SQL
    if search_mrn and search_transplant:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT * 
                FROM [datahub].[Registry_BMT] 
                WHERE MRN = %s AND Number_of_Transplant = %s
            ''', [search_mrn, search_transplant])
            
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            
            if row:
                # Convert row to dictionary
                instance = dict(zip(columns, row))
                search_result = {
                    'type': 'success',
                    'message': f'Found registry entry for MRN: {search_mrn}, Transplant: {search_transplant}'
                }
            else:
                search_result = {
                    'type': 'info',
                    'message': f'No entry found for MRN: {search_mrn}, Transplant: {search_transplant}. You can create a new entry.'
                }
                # Create a new instance with the search parameters
                instance = {'MRN': search_mrn, 'Number_of_Transplant': search_transplant}
    
    if request.method == 'POST':
        form = BMTRegistryForm(request.POST, initial=instance)
        if form.is_valid():
            data = form.cleaned_data
            
            # Check if record exists
            with connection.cursor() as cursor:
                if instance and 'MRN' in instance:  # Update
                    # Build UPDATE query dynamically
                    fields = [f"{field} = %s" for field in data.keys()]
                    values = list(data.values())
                    values.extend([search_mrn, search_transplant])  # Add WHERE clause values
                    
                    query = f'''
                        UPDATE [datahub].[Registry_BMT]
                        SET {", ".join(fields)}
                        WHERE MRN = %s AND Number_of_Transplant = %s
                    '''
                    cursor.execute(query, values)
                    action = 'updated'
                else:  # Insert
                    fields = list(data.keys())
                    placeholders = ['%s'] * len(fields)
                    values = list(data.values())
                    
                    query = f'''
                        INSERT INTO [datahub].[Registry_BMT]
                        ({", ".join(fields)})
                        VALUES ({", ".join(placeholders)})
                    '''
                    cursor.execute(query, values)
                    action = 'created'
            
            # Log the activity
            log_id = int(time.time() * 1000)
            value_string = ', '.join(f"{field}: {value}" for field, value in data.items())
            
            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO [datahub].[KPI_ActivityLog]
                    (log_id, SourcePage, UserName, UserEmail, UserID, MRN, ts, Type, Pending_Status, valuestring)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', [
                    log_id,
                    'BMT Registry',
                    request.user.username,
                    request.user.email,
                    str(request.user.id),
                    data['MRN'],
                    timezone.now(),
                    action,
                    '0',
                    value_string
                ])
            
            messages.success(request, f'Registry successfully {action}.')
            return redirect('registries:bmt_list')
    else:
        form = BMTRegistryForm(initial=instance)
    
    # Get activity log
    activity_log = []
    if search_mrn:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT log_id, SourcePage, UserName, UserEmail, UserID, MRN, 
                       ts as timestamp, Type as action_type, Pending_Status, valuestring
                FROM [datahub].[KPI_ActivityLog] 
                WHERE MRN = %s 
                ORDER BY ts DESC
            ''', [search_mrn])
            
            columns = [col[0] for col in cursor.description]
            activity_log = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    context = {
        'form': form,
        'instance': instance,
        'activity_log': activity_log,
        'search_result': search_result,
        'search_mrn': search_mrn,
        'search_transplant_number': search_transplant,
        'show_form': bool(search_mrn and search_transplant)
    }
    return render(request, 'registries/bmt/form.html', context)

def bmt_list(request):
    search_form = BMTSearchForm(request.GET)
    # Include id in the SELECT statement
    queryset = BMTRegistry.objects.raw('''
        SELECT *, ROW_NUMBER() OVER (ORDER BY MRN, Number_of_Transplant) as id 
        FROM [datahub].[Registry_BMT] 
        ORDER BY MRN, Number_of_Transplant
    ''')
    
    if search_form.is_valid():
        mrn = search_form.cleaned_data.get('mrn')
        transplant_number = search_form.cleaned_data.get('transplant_number')
        
        if mrn:
            queryset = BMTRegistry.objects.raw('''
                SELECT *, ROW_NUMBER() OVER (ORDER BY MRN, Number_of_Transplant) as id 
                FROM [datahub].[Registry_BMT] 
                WHERE MRN LIKE %s 
                ORDER BY MRN, Number_of_Transplant
            ''', ['%' + mrn + '%'])
        if transplant_number:
            queryset = BMTRegistry.objects.raw('''
                SELECT *, ROW_NUMBER() OVER (ORDER BY MRN, Number_of_Transplant) as id 
                FROM [datahub].[Registry_BMT] 
                WHERE Number_of_Transplant = %s 
                ORDER BY MRN, Number_of_Transplant
            ''', [transplant_number])
    
    # Convert queryset to list for pagination
    registry_list = list(queryset)
    paginator = Paginator(registry_list, 25)
    page = request.GET.get('page')
    registries = paginator.get_page(page)
    
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bmt_registry_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        fields = ['MRN', 'Patient_name', 'Number_of_Transplant', 'Service', 'Diagnosis',  # Using exact DB column names
                 'Transplant_Date', 'Last_Follow_up_date', 'Next_Follow_up_Due_Date', 'Patient_Status']
        writer.writerow(fields)
        
        for registry in queryset:
            writer.writerow([getattr(registry, field) for field in fields])
        
        return response
    
    context = {
        'registries': registries,
        'search_form': search_form
    }
    return render(request, 'registries/bmt/list.html', context)

def bmt_dashboard(request):
    today = timezone.now().date()
    
    # Calculate survival rate
    total_patients = BMTRegistry.objects.count()
    alive_patients = BMTRegistry.objects.filter(death_date__isnull=True).count()
    survival_rate = round((alive_patients / total_patients * 100), 1) if total_patients > 0 else 0
    
    # Get transplants trend data
    transplants_trend = (
        BMTRegistry.objects
        .annotate(month=TruncMonth('transplant_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    context = {
        'total_registries': total_patients,
        'total_active': alive_patients,
        'transplants_this_year': BMTRegistry.objects.filter(
            transplant_date__year=today.year
        ).count(),
        'survival_rate': survival_rate,
        'transplants_trend': {
            'labels': [entry['month'].strftime('%b %Y') for entry in transplants_trend],
            'data': [entry['count'] for entry in transplants_trend]
        }
    }
    return render(request, 'registries/bmt/dashboard.html', context)

def bmt_followup(request):
    today = timezone.now().date()
    week_from_now = today + timedelta(days=7)
    month_from_now = today + timedelta(days=30)

    # Base queryset using raw SQL for date calculations
    queryset = BMTRegistry.objects.raw('''
        SELECT *, 
            CONCAT(MRN, '_', Number_of_Transplant) as id,
            DATEDIFF(day, GETDATE(), Next_Follow_up_Due_Date) as days_until,
            ABS(DATEDIFF(day, GETDATE(), Next_Follow_up_Due_Date)) as days_until_abs,
            CASE 
                WHEN Next_Follow_up_Due_Date < GETDATE() THEN 1 
                ELSE 0 
            END as is_overdue,
            CASE 
                WHEN Next_Follow_up_Due_Date <= DATEADD(day, 7, GETDATE()) 
                AND Next_Follow_up_Due_Date >= GETDATE() THEN 1 
                ELSE 0 
            END as is_due_soon,
            CASE 
                WHEN Next_Follow_up_Due_Date <= DATEADD(day, 30, GETDATE()) 
                AND Next_Follow_up_Due_Date >= GETDATE() THEN 1 
                ELSE 0 
            END as is_due_this_month
        FROM [datahub].[Registry_BMT]
        WHERE death_date IS NULL 
        AND Last_Follow_up_date IS NOT NULL
        ORDER BY Next_Follow_up_Due_Date
    ''')

    # Convert queryset to list for stats calculation
    registry_list = list(queryset)
    
    stats = {
        'due_this_week': len([r for r in registry_list if r.is_due_soon]),
        'due_this_month': len([r for r in registry_list if r.is_due_this_month]),
        'overdue': len([r for r in registry_list if r.is_overdue]),
        'total_active': len(registry_list),
    }

    # Handle filters
    status_filter = request.GET.get('status')
    service_filter = request.GET.get('service')
    search_term = request.GET.get('search')

    filtered_list = registry_list
    if status_filter:
        if status_filter == 'overdue':
            filtered_list = [r for r in registry_list if r.is_overdue]
        elif status_filter == 'due':
            filtered_list = [r for r in registry_list if r.is_due_soon]

    if service_filter:
        filtered_list = [r for r in filtered_list if r.service == service_filter]

    if search_term:
        filtered_list = [r for r in filtered_list if 
            search_term.lower() in r.MRN.lower() or 
            search_term.lower() in r.patient_name.lower()]

    # Handle CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bmt_followups_{today.strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        headers = ['MRN', 'Patient Name', 'Service', 'Last Follow-up', 'Next Due Date', 'Days Until/Overdue', 'Status']
        writer.writerow(headers)
        
        for followup in filtered_list:
            status = 'Overdue' if followup.is_overdue else 'Due Soon' if followup.is_due_soon else 'Scheduled'
            writer.writerow([
                followup.MRN,
                followup.patient_name,
                followup.service,
                followup.last_followup_date.strftime('%Y-%m-%d') if followup.last_followup_date else '',
                followup.next_followup_date.strftime('%Y-%m-%d') if followup.next_followup_date else '',
                f"{followup.days_until_abs} days {'overdue' if followup.is_overdue else 'until'}",
                status
            ])
        
        return response

    # Pagination
    paginator = Paginator(filtered_list, 25)
    page = request.GET.get('page')
    followups = paginator.get_page(page)

    context = {
        'followups': followups,
        **stats
    }
    return render(request, 'registries/bmt/followup.html', context)

def bmt_followup_complete(request, mrn, transplant_number):
    if request.method == 'POST':
        registry = get_object_or_404(BMTRegistry, MRN=mrn, transplant_number=transplant_number)
        
        # Update follow-up dates
        registry.last_followup_date = timezone.now().date()
        registry.next_followup_date = registry.last_followup_date + timedelta(days=30)
        registry.save()
        
        # Log the activity
        BMTActivityLog.objects.create(
            log_id=int(time.time() * 1000),
            source_page='BMT Registry',
            username=request.user.username,
            user_email=request.user.email,
            user_id=str(request.user.id),
            mrn=registry.MRN,
            timestamp=timezone.now(),
            action_type='follow_up_completed',
            pending_status='0',
            value_string=f"Follow-up completed on {registry.last_followup_date}"
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400) 