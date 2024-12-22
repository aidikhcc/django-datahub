from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from .models import Event, EventComment, ModificationLog, EventAssignment
from .decorators import debug_login_required, qmo_required
from .utils import retrieve_patient_info
from django.db import transaction
import json
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone

@debug_login_required
def event_home(request):
    """Home page for Event Reporting system"""
    return render(request, 'event_reporting/event_home.html')

@debug_login_required
def event_form(request, event_number=None):
    """Create or edit an event report"""
    print(f"Entering event_form view")
    print(f"Method: {request.method}")
    print(f"Event number: {event_number}")
    print(f"POST data: {request.POST}")
    print(f"GET data: {request.GET}")
    
    try:
        event = None
        search_mrn = request.GET.get('search_mrn')
        search_result = None
        
        # Handle POST request for form submission
        if request.method == 'POST':
            with transaction.atomic():
                # Get or create event instance
                if event_number:
                    event = get_object_or_404(Event, event_number=event_number)
                else:
                    event = Event()
                
                # Required fields
                event.MRN = request.POST.get('MRN')
                event.event_date = request.POST.get('event_date')
                event.department_initiated = request.POST.get('department_initiated')
                event.supervisor_name = request.POST.get('supervisor_name')
                event.event_description = request.POST.get('event_description')
                event.immediate_action = request.POST.get('immediate_action')
                
                # Optional fields
                event.patient_name = request.POST.get('patient_name')
                event.dob = request.POST.get('dob') or None
                event.gender = request.POST.get('gender')
                event.nationality = request.POST.get('nationality')
                event.diagnosis = request.POST.get('diagnosis')
                event.floor_unit = request.POST.get('floor_unit')
                event.room = request.POST.get('room')
                event.supervisor_email = request.POST.get('supervisor_email')
                event.good_catch_event = request.POST.get('good_catch_event') == 'on'
                event.pending = request.POST.get('pending', 'on') == 'on'
                
                event.save()
                messages.success(request, 'Event saved successfully!')
                return redirect('event_reporting:event_list')
        
        # Handle GET request for displaying form
        elif event_number:
            event = get_object_or_404(Event, event_number=event_number)
            print(f"Found existing event: {event}")
        elif search_mrn:
            # Get patient info for new event
            patient_info = retrieve_patient_info(search_mrn)
            if patient_info:
                event = Event(
                    MRN=search_mrn,
                    patient_name=patient_info['name'],
                    dob=patient_info['dob'],
                    gender=patient_info['gender'],
                    nationality=patient_info['nationality'],
                    age=patient_info['age'],
                    pending=True
                )
                search_result = {
                    'type': 'success',
                    'message': f'Patient information retrieved. You can create a new event.'
                }
            else:
                search_result = {
                    'type': 'warning',
                    'message': f'No patient found with MRN: {search_mrn}'
                }
        
        context = {
            'event': event,
            'search_mrn': search_mrn,
            'search_result': search_result,
            'debug': settings.DEBUG,
        }
        print(f"Rendering template with context: {context}")
        
        return render(request, 'event_reporting/event_form.html', context)
        
    except Exception as e:
        print(f"Error in event_form view: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('event_reporting:event_list')

@qmo_required('view_all_events')
def event_list(request):
    """List all event reports with filtering"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get filter parameters
    department = request.GET.get('department')
    date_range = request.GET.get('date_range')
    scoring = request.GET.get('scoring')
    
    # Start with all events
    events = Event.objects.all()
    
    # Apply filters
    if department:
        events = events.filter(department_initiated=department)
    
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            events = events.filter(event_date=today)
        elif date_range == 'week':
            week_ago = today - timedelta(days=7)
            events = events.filter(event_date__gte=week_ago)
        elif date_range == 'month':
            month_ago = today - timedelta(days=30)
            events = events.filter(event_date__gte=month_ago)
    
    if scoring:
        events = events.filter(initial_scoring=scoring)
    
    # Calculate totals
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    totals = {
        'total': Event.objects.count(),
        'good_catch': Event.objects.filter(good_catch_event=True).count(),
        'this_month': Event.objects.filter(event_date__gte=month_start).count(),
        'today': Event.objects.filter(event_date=today).count(),
        'scored': Event.objects.exclude(final_score__isnull=True).count(),
        'closed': Event.objects.filter(event_closed=True).count(),
    }
    
    # Get unique departments for filter
    departments = Event.objects.values('department_initiated').distinct()
    
    # Check if any filters are active
    any_filters_active = any([department, date_range, scoring])
    
    context = {
        'events': events.order_by('-event_date'),
        'totals': totals,
        'departments': departments,
        'selected_filters': {
            'department': department,
            'date_range': date_range,
            'scoring': scoring,
        },
        'any_filters_active': any_filters_active,
    }
    
    return render(request, 'event_reporting/event_list.html', context)

@debug_login_required
def incident_home(request):
    """Placeholder for Incident Reporting home page"""
    return render(request, 'event_reporting/incident_home.html')

def add_comment(request, event_number):
    if request.method == 'POST':
        event = get_object_or_404(Event, event_number=event_number)
        comment_text = request.POST.get('comment')
        
        if comment_text:
            EventComment.objects.create(
                event=event,
                comment=comment_text,
                created_by=request.user
            )
            messages.success(request, 'Comment added successfully.')
        else:
            messages.error(request, 'Comment cannot be empty.')
            
    return redirect('event_reporting:event_list')

def event_new(request):
    if request.method == 'POST':
        try:
            # Handle event_date
            event_date = request.POST.get('event_date')
            if event_date:
                event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            else:
                event_date = None

            # Handle dob
            dob = request.POST.get('dob')
            if dob:
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            else:
                dob = None

            # Create event object
            event = Event(
                event_date=event_date,
                dob=dob,
                # ... other fields ...
            )
            event.save()
            
            return redirect('event_reporting:event_list')
            
        except ValidationError as e:
            messages.error(request, f"Validation error: {e}")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
    
    return render(request, 'event_reporting/event_form.html')

@debug_login_required
def event_view(request, event_number):
    """View a completed event report"""
    event = get_object_or_404(Event, event_number=event_number)
    if event.pending:
        return redirect('event_reporting:event_form', event_number=event_number)
    
    return render(request, 'event_reporting/event_view.html', {
        'event': event,
    })

@debug_login_required
def add_comment(request, event_number):
    """Add a comment to an event"""
    if request.method == 'POST':
        event = get_object_or_404(Event, event_number=event_number)
        comment_text = request.POST.get('comment')
        
        if comment_text:
            EventComment.objects.create(
                event=event,
                comment=comment_text,
                created_by=request.user
            )
            messages.success(request, 'Comment added successfully.')
        else:
            messages.error(request, 'Comment cannot be empty.')
    
    return redirect('event_reporting:event_list')

@debug_login_required
def assign_event(request, event_number):
    """Assign an event to a user"""
    if request.method == 'POST':
        event = get_object_or_404(Event, event_number=event_number)
        user_email = request.POST.get('user_email')
        
        if user_email:
            EventAssignment.objects.create(
                event=event,
                user_email=user_email
            )
            messages.success(request, f'Event assigned to {user_email}')
        else:
            messages.error(request, 'User email is required')
    
    return redirect('event_reporting:event_list')

@qmo_required('view_qmo_dashboard')
def qmo_dashboard(request):
    """QMO Dashboard view"""
    # Get statistics and data for dashboard
    total_events = Event.objects.count()
    pending_events = Event.objects.filter(pending=True).count()
    completed_events = Event.objects.filter(pending=False).count()
    good_catch_events = Event.objects.filter(good_catch_event=True).count()
    
    # Get department statistics
    department_stats = Event.objects.values('department_initiated')\
        .annotate(count=models.Count('event_number'))\
        .order_by('-count')
    
    context = {
        'total_events': total_events,
        'pending_events': pending_events,
        'completed_events': completed_events,
        'good_catch_events': good_catch_events,
        'department_stats': department_stats,
    }
    
    return render(request, 'event_reporting/qmo_dashboard.html', context)

@qmo_required('export_reports')
def export_reports(request):
    """Export events data"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="events_export_{datetime.now().strftime("%Y%m%d")}.csv"'},
    )
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Event Number',
        'MRN',
        'Patient Name',
        'Event Date',
        'Department',
        'Status',
        'Description',
        'Immediate Action',
        'Created At',
        'Updated At'
    ])
    
    # Write data rows
    events = Event.objects.all().order_by('-event_date')
    for event in events:
        writer.writerow([
            event.event_number,
            event.MRN,
            event.patient_name,
            event.event_date,
            event.department_initiated,
            'Pending' if event.pending else 'Completed',
            event.event_description,
            event.immediate_action,
            event.created_at,
            event.updated_at
        ])
    
    return response

@qmo_required('manage_events')
def qmo_scoring(request, event_number):
    event = get_object_or_404(Event, event_number=event_number)
    
    if request.method == 'POST':
        event.final_score = request.POST.get('final_score')
        event.likelihood = request.POST.get('likelihood')
        event.consequence = request.POST.get('consequence')
        event.risk_calculated = request.POST.get('risk_calculated')
        event.adhoc_committee_done = request.POST.get('adhoc_committee_done') == 'on'
        event.event_closed = request.POST.get('event_closed') == 'on'
        event.qmo_notes = request.POST.get('qmo_notes')
        event.scored_by = request.user.email
        event.scored_at = timezone.now()
        event.save()
        
        messages.success(request, 'QMO scoring saved successfully.')
        return redirect('event_reporting:event_list')
    
    context = {
        'event': event,
        'final_score_choices': Event.FINAL_SCORE_CHOICES,
        'likelihood_choices': Event.LIKELIHOOD_CHOICES,
        'consequence_choices': Event.CONSEQUENCE_CHOICES,
    }
    
    return render(request, 'event_reporting/qmo_scoring.html', context)