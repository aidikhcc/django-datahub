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
from django.db import connection

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
    
    try:
        event = None
        search_mrn = request.GET.get('search_mrn')
        search_result = None
        
        # Add at the start of the view
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@version;")
            db_version = cursor.fetchone()[0]
            print(f"Connected to database: {db_version}")
        
        # Handle POST request for form submission
        if request.method == 'POST':
            print("Processing POST request")
            print("POST data received:")
            for key, value in request.POST.items():
                print(f"{key}: {value}")
            with transaction.atomic():
                # Get or create event instance
                if event_number:
                    print(f"Updating existing event {event_number}")
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT 
                                event_number, event_date, report_date, MRN, patient_name, 
                                dob, gender, age, nationality, diagnosis, floor_unit, room,
                                department_initiated, supervisor_name, supervisor_email,
                                event_description, immediate_action, good_catch_event, pending,
                                created_at, updated_at, final_score, likelihood, consequence,
                                risk_calculated, adhoc_committee_done, event_closed,
                                qmo_notes, scored_by, scored_at, type_of_error,
                                recommended_action_plan, action_plan_others,
                                supervisor_comments, department_unit_involved,
                                department_unit_involved_2, initial_scoring,
                                is_bmt_patient, bmt_physician_name, bmt_occurrence_category,
                                bmt_patient_donor_notified, bmt_patient_donor_notified_time,
                                bmt_ctag_reviewed, bmt_ctag_reviewed_time,
                                bmt_program_director_notified, bmt_program_director_time,
                                bmt_program_director_date, bmt_attending_notified,
                                bmt_attending_time, bmt_attending_date,
                                bmt_quality_council_date, bmt_comments
                            FROM [datahub].[Event_Reports]
                            WHERE event_number = %s
                        """, [event_number])
                        
                        row = cursor.fetchone()
                        if not row:
                            raise Http404("Event not found")
                            
                        event = Event()
                        event.event_number = row[0]
                        event.event_date = row[1]
                        event.report_date = row[2]
                        event.MRN = row[3]
                        event.patient_name = row[4]
                        event.dob = row[5]
                        event.gender = row[6]
                        event.age = row[7]
                        event.nationality = row[8]
                        event.diagnosis = row[9]
                        event.floor_unit = row[10]
                        event.room = row[11]
                        event.department_initiated = row[12]
                        event.supervisor_name = row[13]
                        event.supervisor_email = row[14]
                        event.event_description = row[15]
                        event.immediate_action = row[16]
                        event.good_catch_event = row[17]
                        event.pending = row[18]
                        event.created_at = row[19]
                        event.updated_at = row[20]
                        event.final_score = row[21]
                        event.likelihood = row[22]
                        event.consequence = row[23]
                        event.risk_calculated = row[24]
                        event.adhoc_committee_done = row[25]
                        event.event_closed = row[26]
                        event.qmo_notes = row[27]
                        event.scored_by = row[28]
                        event.scored_at = row[29]
                        event.type_of_error = row[30]
                        event.recommended_action_plan = row[31]
                        event.action_plan_others = row[32]
                        event.supervisor_comments = row[33]
                        event.department_unit_involved = row[34]
                        event.department_unit_involved_2 = row[35]
                        event.initial_scoring = row[36]
                        event.is_bmt_patient = row[37]
                        event.bmt_physician_name = row[38]
                        event.bmt_occurrence_category = row[39]
                        event.bmt_patient_donor_notified = row[40]
                        event.bmt_patient_donor_notified_time = row[41]
                        event.bmt_ctag_reviewed = row[42]
                        event.bmt_ctag_reviewed_time = row[43]
                        event.bmt_program_director_notified = row[44]
                        event.bmt_program_director_time = row[45]
                        event.bmt_program_director_date = row[46]
                        event.bmt_attending_notified = row[47]
                        event.bmt_attending_time = row[48]
                        event.bmt_attending_date = row[49]
                        event.bmt_quality_council_date = row[50]
                        event.bmt_comments = row[51]
                        
                        # Get categories for this event
                        cursor.execute("""
                            SELECT category_type, subcategory
                            FROM [datahub].[Event_Categories]
                            WHERE event_number = %s
                        """, [event_number])
                        categories = cursor.fetchall()
                        
                        # Instead of direct assignment, store categories as a list property
                        event._categories = [{'type': cat[0], 'subcategory': cat[1]} for cat in categories]
                        
                        # Add a method to access categories
                        def get_categories(self):
                            return getattr(self, '_categories', [])
                        event.get_categories = get_categories.__get__(event)
                else:
                    print("Creating new event")
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
                
                # Add these fields
                event.department_unit_involved = request.POST.get('department_unit_involved')
                event.department_unit_involved_2 = request.POST.get('department_unit_involved_2')
                event.initial_scoring = request.POST.get('initial_scoring')
                
                # Handle categories
                primary_categories = request.POST.getlist('primary_category')
                subcategories = request.POST.getlist('subcategory')

                # Delete existing categories
                with connection.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM [datahub].[Event_Categories]
                        WHERE event_number = %s
                    """, [event.event_number])

                # Save new categories
                for category_type, subcategory in zip(primary_categories, subcategories):
                    if category_type and subcategory:
                        # First insert the category
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO [datahub].[Event_Categories]
                                (event_number, category_type, subcategory, created_at, updated_at)
                                VALUES (%s, %s, %s, GETDATE(), GETDATE());
                                SELECT SCOPE_IDENTITY();
                            """, [event.event_number, category_type, subcategory])
                            category_id = cursor.fetchone()[0]
                            
                            # If this is a surgery category, save the details
                            if category_type == 'surgery_related':
                                cursor.execute("""
                                    INSERT INTO [datahub].[Surgery_Details]
                                    (event_number, category_id, post_op_complication, 
                                     intraoperative_complication, cancelled_procedure,
                                     cancelled_procedure_location, equipment_cause,
                                     hospital_related, medical_cause, patient_related,
                                     staff_related)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, [
                                    event.event_number,
                                    category_id,
                                    request.POST.get('post_op_complications'),
                                    request.POST.get('intraoperative_complications'),
                                    request.POST.get('cancelled_procedure'),
                                    request.POST.get('cancelled_procedure_location'),
                                    request.POST.get('equipment_causes'),
                                    request.POST.get('hospital_related'),
                                    request.POST.get('medical_causes'),
                                    request.POST.get('patient_related'),
                                    request.POST.get('staff_related')
                                ])
                
                # Add debug print before save
                print("About to save event with data:", {
                    'MRN': event.MRN,
                    'event_date': event.event_date,
                    'department_initiated': event.department_initiated,
                    'department_unit_involved': event.department_unit_involved,
                    'department_unit_involved_2': event.department_unit_involved_2,
                    'initial_scoring': event.initial_scoring,
                    'supervisor_name': event.supervisor_name,
                    'pending': event.pending
                })
                
                try:
                    event.save()
                    print("Event saved successfully")
                    messages.success(request, 'Event saved successfully!')
                    return redirect('event_reporting:event_list')
                except Exception as save_error:
                    print(f"Error saving event: {str(save_error)}")
                    raise  # Re-raise the exception to be caught by outer try block
        
        # Handle GET request for displaying form
        elif event_number:
            # Get fresh data from database using raw SQL
            with connection.cursor() as cursor:
                # Get event data
                cursor.execute("""
                    SELECT 
                        event_number, event_date, report_date, MRN, patient_name, 
                        dob, gender, age, nationality, diagnosis, floor_unit, room,
                        department_initiated, supervisor_name, supervisor_email,
                        event_description, immediate_action, good_catch_event, pending,
                        created_at, updated_at, final_score, likelihood, consequence,
                        risk_calculated, adhoc_committee_done, event_closed,
                        qmo_notes, scored_by, scored_at, type_of_error,
                        recommended_action_plan, action_plan_others,
                        supervisor_comments, department_unit_involved,
                        department_unit_involved_2, initial_scoring,
                        is_bmt_patient, bmt_physician_name, bmt_occurrence_category,
                        bmt_patient_donor_notified, bmt_patient_donor_notified_time,
                        bmt_ctag_reviewed, bmt_ctag_reviewed_time,
                        bmt_program_director_notified, bmt_program_director_time,
                        bmt_program_director_date, bmt_attending_notified,
                        bmt_attending_time, bmt_attending_date,
                        bmt_quality_council_date, bmt_comments
                    FROM [datahub].[Event_Reports]
                    WHERE event_number = %s
                """, [event_number])
                
                row = cursor.fetchone()
                if row:
                    # Create Event object from raw data
                    event = Event()
                    event.event_number = row[0]
                    event.event_date = row[1]
                    event.report_date = row[2]
                    event.MRN = row[3]
                    event.patient_name = row[4]
                    event.dob = row[5]
                    event.gender = row[6]
                    event.age = row[7]
                    event.nationality = row[8]
                    event.diagnosis = row[9]
                    event.floor_unit = row[10]
                    event.room = row[11]
                    event.department_initiated = row[12]
                    event.supervisor_name = row[13]
                    event.supervisor_email = row[14]
                    event.event_description = row[15]
                    event.immediate_action = row[16]
                    event.good_catch_event = row[17]
                    event.pending = row[18]
                    event.created_at = row[19]
                    event.updated_at = row[20]
                    event.final_score = row[21]
                    event.likelihood = row[22]
                    event.consequence = row[23]
                    event.risk_calculated = row[24]
                    event.adhoc_committee_done = row[25]
                    event.event_closed = row[26]
                    event.qmo_notes = row[27]
                    event.scored_by = row[28]
                    event.scored_at = row[29]
                    event.type_of_error = row[30]
                    event.recommended_action_plan = row[31]
                    event.action_plan_others = row[32]
                    event.supervisor_comments = row[33]
                    event.department_unit_involved = row[34]
                    event.department_unit_involved_2 = row[35]
                    event.initial_scoring = row[36]
                    event.is_bmt_patient = row[37]
                    event.bmt_physician_name = row[38]
                    event.bmt_occurrence_category = row[39]
                    event.bmt_patient_donor_notified = row[40]
                    event.bmt_patient_donor_notified_time = row[41]
                    event.bmt_ctag_reviewed = row[42]
                    event.bmt_ctag_reviewed_time = row[43]
                    event.bmt_program_director_notified = row[44]
                    event.bmt_program_director_time = row[45]
                    event.bmt_program_director_date = row[46]
                    event.bmt_attending_notified = row[47]
                    event.bmt_attending_time = row[48]
                    event.bmt_attending_date = row[49]
                    event.bmt_quality_council_date = row[50]
                    event.bmt_comments = row[51]
                    
                    # Get categories for this event
                    cursor.execute("""
                        SELECT category_type, subcategory
                        FROM [datahub].[Event_Categories]
                        WHERE event_number = %s
                    """, [event_number])
                    categories = cursor.fetchall()
                    
                    # Instead of direct assignment, store categories as a list property
                    event._categories = [{'type': cat[0], 'subcategory': cat[1]} for cat in categories]
                    
                    # Add a method to access categories
                    def get_categories(self):
                        return getattr(self, '_categories', [])
                    event.get_categories = get_categories.__get__(event)
                    
                    # After retrieving categories
                    for category in event._categories:
                        if category['type'] == 'surgery_related':
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    SELECT post_op_complication, intraoperative_complication,
                                           cancelled_procedure, cancelled_procedure_location,
                                           equipment_cause, hospital_related, medical_cause,
                                           patient_related, staff_related
                                    FROM [datahub].[Surgery_Details]
                                    WHERE event_number = %s AND category_id = %s
                                """, [event.event_number, category['id']])
                                surgery_details = cursor.fetchone()
                                if surgery_details:
                                    category['surgery_details'] = {
                                        'post_op_complication': surgery_details[0],
                                        'intraoperative_complication': surgery_details[1],
                                        'cancelled_procedure': surgery_details[2],
                                        'cancelled_procedure_location': surgery_details[3],
                                        'equipment_cause': surgery_details[4],
                                        'hospital_related': surgery_details[5],
                                        'medical_cause': surgery_details[6],
                                        'patient_related': surgery_details[7],
                                        'staff_related': surgery_details[8]
                                    }
                else:
                    from django.http import Http404
                    raise Http404("Event not found")
            
            print(f"Found existing event: {event}")
            print(f"Supervisor name: {event.supervisor_name}")
        
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
    
    # Build the SQL query with only existing columns
    with connection.cursor() as cursor:
        sql = """
            SELECT 
                event_number, event_date, MRN, patient_name, 
                department_initiated, supervisor_name,
                event_description, immediate_action,
                good_catch_event, pending, final_score,
                created_at, updated_at
            FROM [datahub].[Event_Reports]
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if department:
            sql += " AND department_initiated = %s"
            params.append(department)
        
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                sql += " AND event_date = %s"
                params.append(today)
            elif date_range == 'week':
                sql += " AND event_date >= %s"
                params.append(today - timedelta(days=7))
            elif date_range == 'month':
                sql += " AND event_date >= %s"
                params.append(today - timedelta(days=30))
        
        if scoring:
            sql += " AND final_score = %s"
            params.append(scoring)
        
        sql += " ORDER BY event_date DESC"
        
        # Execute query
        cursor.execute(sql, params)
        
        # Convert to list of Event objects
        events = []
        for row in cursor.fetchall():
            event = Event()
            event.event_number = row[0]
            event.event_date = row[1]
            event.MRN = row[2]
            event.patient_name = row[3]
            event.department_initiated = row[4]
            event.supervisor_name = row[5]
            event.event_description = row[6]
            event.immediate_action = row[7]
            event.good_catch_event = row[8]
            event.pending = row[9]
            event.final_score = row[10]
            event.created_at = row[11]
            event.updated_at = row[12]
            events.append(event)
        
        # Get totals
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN good_catch_event = 1 THEN 1 ELSE 0 END) as good_catch,
                SUM(CASE WHEN event_date >= DATEADD(month, -1, GETDATE()) THEN 1 ELSE 0 END) as this_month,
                SUM(CASE WHEN event_date = CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END) as today
            FROM [datahub].[Event_Reports]
        """)
        totals_row = cursor.fetchone()
        totals = {
            'total': totals_row[0] or 0,
            'good_catch': totals_row[1] or 0,
            'this_month': totals_row[2] or 0,
            'today': totals_row[3] or 0,
        }
        
        # Get unique departments for filter
        cursor.execute("""
            SELECT DISTINCT department_initiated 
            FROM [datahub].[Event_Reports] 
            WHERE department_initiated IS NOT NULL
            ORDER BY department_initiated
        """)
        departments = [{'department_initiated': row[0]} for row in cursor.fetchall()]
    
    context = {
        'events': events,
        'totals': totals,
        'departments': departments,
        'selected_filters': {
            'department': department,
            'date_range': date_range,
            'scoring': scoring,
        },
        'any_filters_active': any([department, date_range, scoring]),
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