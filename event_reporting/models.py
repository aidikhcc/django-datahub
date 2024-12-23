from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.conf import settings

class Event(models.Model):
    # Floor/Unit Choices
    FLOOR_UNIT_CHOICES = [
        ("Sheikh Khalifa 7th", "Sheikh Khalifa 7th"),
        ("Sheikh Khalifa 6th", "Sheikh Khalifa 6th"),
        ("Sheikh Khalifa 2nd", "Sheikh Khalifa 2nd"),
        ("Sheikh Khalifa 5th", "Sheikh Khalifa 5th"),
        ("Nizar AL-Naqeeb 1st", "Nizar AL-Naqeeb 1st"),
        ("Sheikh Khalifa 8th", "Sheikh Khalifa 8th"),
        ("Sheikh Khalifa 4th", "Sheikh Khalifa 4th"),
        ("MAIN OFFICE", "MAIN OFFICE"),
        ("Early Detection", "Early Detection"),
        ("Nizar AL-Naqeeb 2nd", "Nizar AL-Naqeeb 2nd"),
        ("EMPLOYEES CLINIC", "EMPLOYEES CLINIC"),
        ("Nizar AL-Naqeeb Basmant", "Nizar AL-Naqeeb Basmant"),
        ("Nizar Al Naqeeb", "Nizar Al Naqeeb"),
        ("King Salman GF", "King Salman GF"),
        ("Other", "Other")
    ]

    # Diagnosis Choices
    DIAGNOSIS_CHOICES = [
        ("Lung", "Lung"),
        ("Neuroendocrine tumor", "Neuroendocrine tumor"),
        ("GIST", "GIST"),
        ("Chronic granulomatous disease", "Chronic granulomatous disease"),
        ("Submandibular tumor", "Submandibular tumor"),
        ("Unknown primary", "Unknown primary"),
        ("Skin", "Skin"),
        ("Melanoma", "Melanoma"),
        ("Tracheal", "Tracheal"),
        ("Autoimmune lymphoproliferative syndrome", "Autoimmune lymphoproliferative syndrome"),
        ("Glioblastoma", "Glioblastoma"),
        ("Myelofibrosis", "Myelofibrosis"),
        ("Urothelial carcinoma", "Urothelial carcinoma"),
        ("Penile", "Penile"),
        ("Choriocarcinoma", "Choriocarcinoma"),
        ("Pituitary", "Pituitary"),
        ("Myelodysplastic syndrome", "Myelodysplastic syndrome"),
        ("Aplastic", "Aplastic")
    ]

    # Event Categories
    medication_related = models.CharField(max_length=255, blank=True, null=True)
    iv_blood_related = models.CharField(max_length=255, blank=True, null=True)
    laboratory_related = models.CharField(max_length=255, blank=True, null=True)
    surgery_related = models.CharField(max_length=255, blank=True, null=True)
    documentation_related = models.CharField(max_length=255, blank=True, null=True)
    equipment_related = models.CharField(max_length=255, blank=True, null=True)
    patient_safety_related = models.CharField(max_length=255, blank=True, null=True)
    admission_related = models.CharField(max_length=255, blank=True, null=True)

    # Event Identification
    event_number = models.AutoField(primary_key=True)
    event_date = models.DateField(null=True, blank=True)
    report_date = models.DateField(auto_now_add=True)
    
    # Patient Information
    MRN = models.CharField(max_length=50)
    patient_name = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    diagnosis = models.CharField(max_length=100, choices=DIAGNOSIS_CHOICES, blank=True, null=True)
    floor_unit = models.CharField(max_length=100, choices=FLOOR_UNIT_CHOICES, blank=True, null=True)
    room = models.CharField(max_length=50, blank=True, null=True)
    
    # Event Details
    department_initiated = models.CharField(max_length=100)
    supervisor_name = models.CharField(max_length=255)
    supervisor_email = models.EmailField(blank=True, null=True)
    
    # Description and Actions
    event_description = models.TextField()
    immediate_action = models.TextField()
    
    # Status and Classification
    good_catch_event = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # QMO Scoring Fields
    FINAL_SCORE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
        ('H', 'H'),
        ('I', 'I'),
        ('NO', 'No score'),
    ]

    LIKELIHOOD_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]

    CONSEQUENCE_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]

    final_score = models.CharField(max_length=2, choices=FINAL_SCORE_CHOICES, null=True, blank=True)
    likelihood = models.CharField(max_length=1, choices=LIKELIHOOD_CHOICES, null=True, blank=True)
    consequence = models.CharField(max_length=1, choices=CONSEQUENCE_CHOICES, null=True, blank=True)
    risk_calculated = models.TextField(null=True, blank=True)
    adhoc_committee_done = models.BooleanField(default=False)
    event_closed = models.BooleanField(default=False)
    qmo_notes = models.TextField(null=True, blank=True)
    scored_by = models.EmailField(null=True, blank=True)
    scored_at = models.DateTimeField(null=True, blank=True)

    # New fields
    type_of_error = models.CharField(max_length=100, null=True, blank=True)
    recommended_action_plan = models.CharField(max_length=100, null=True, blank=True)
    action_plan_others = models.TextField(null=True, blank=True)
    supervisor_comments = models.TextField(null=True, blank=True)
    
    # Department fields
    department_unit_involved = models.CharField(max_length=100, null=True, blank=True)
    department_unit_involved_2 = models.CharField(max_length=100, null=True, blank=True)
    
    # Initial scoring
    initial_scoring = models.CharField(max_length=20, null=True, blank=True)
    
    # BMT fields
    is_bmt_patient = models.BooleanField(default=False)
    bmt_physician_name = models.CharField(max_length=100, null=True, blank=True)
    bmt_occurrence_category = models.CharField(max_length=50, null=True, blank=True)
    bmt_patient_donor_notified = models.CharField(max_length=10, null=True, blank=True)
    bmt_patient_donor_notified_time = models.TimeField(null=True, blank=True)
    bmt_ctag_reviewed = models.CharField(max_length=10, null=True, blank=True)
    bmt_ctag_reviewed_time = models.TimeField(null=True, blank=True)
    bmt_program_director_notified = models.CharField(max_length=10, null=True, blank=True)
    bmt_program_director_time = models.TimeField(null=True, blank=True)
    bmt_program_director_date = models.DateField(null=True, blank=True)
    bmt_attending_notified = models.CharField(max_length=10, null=True, blank=True)
    bmt_attending_time = models.TimeField(null=True, blank=True)
    bmt_attending_date = models.DateField(null=True, blank=True)
    bmt_quality_council_date = models.DateField(null=True, blank=True)
    bmt_comments = models.TextField(null=True, blank=True)

    class Meta:
        db_table = '[datahub].[Event_Reports]'
        managed = False

    def save(self, *args, **kwargs):
        print("Saving event with data:", {
            'event_number': self.event_number,
            'MRN': self.MRN,
            'event_date': self.event_date,
            'department_initiated': self.department_initiated,
            'supervisor_name': self.supervisor_name,
            'pending': self.pending
        })
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                if self.event_number:
                    sql = """
                        UPDATE [datahub].[Event_Reports]
                        SET MRN = %s,
                            event_date = %s,
                            department_initiated = %s,
                            department_unit_involved = %s,
                            department_unit_involved_2 = %s,
                            initial_scoring = %s,
                            supervisor_name = %s,
                            event_description = %s,
                            immediate_action = %s,
                            patient_name = %s,
                            dob = %s,
                            gender = %s,
                            nationality = %s,
                            diagnosis = %s,
                            floor_unit = %s,
                            room = %s,
                            supervisor_email = %s,
                            good_catch_event = %s,
                            pending = %s,
                            updated_at = GETDATE()
                        WHERE event_number = %s
                    """
                    params = [
                        self.MRN,
                        self.event_date,
                        self.department_initiated,
                        self.department_unit_involved,
                        self.department_unit_involved_2,
                        self.initial_scoring,
                        self.supervisor_name,
                        self.event_description,
                        self.immediate_action,
                        self.patient_name,
                        self.dob,
                        self.gender,
                        self.nationality,
                        self.diagnosis,
                        self.floor_unit,
                        self.room,
                        self.supervisor_email,
                        1 if self.good_catch_event else 0,
                        1 if self.pending else 0,
                        self.event_number
                    ]
                    print("Executing SQL with params:", params)
                    cursor.execute(sql, params)
                    print(f"Rows affected: {cursor.rowcount}")
                else:
                    # Insert new event
                    sql = """
                        INSERT INTO [datahub].[Event_Reports] (
                            MRN, event_date, department_initiated, supervisor_name,
                            event_description, immediate_action, patient_name, dob,
                            gender, nationality, diagnosis, floor_unit, room,
                            supervisor_email, good_catch_event, pending,
                            type_of_error, recommended_action_plan, action_plan_others,
                            supervisor_comments, department_unit_involved,
                            department_unit_involved_2, initial_scoring,
                            is_bmt_patient, bmt_physician_name, bmt_occurrence_category,
                            bmt_patient_donor_notified, bmt_patient_donor_notified_time,
                            bmt_ctag_reviewed, bmt_ctag_reviewed_time,
                            bmt_program_director_notified, bmt_program_director_time,
                            bmt_program_director_date, bmt_attending_notified,
                            bmt_attending_time, bmt_attending_date,
                            bmt_quality_council_date, bmt_comments,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, GETDATE(), GETDATE()
                        );
                        SELECT SCOPE_IDENTITY();
                    """
                    params = [
                        self.MRN,
                        self.event_date,
                        self.department_initiated,
                        self.supervisor_name,
                        self.event_description,
                        self.immediate_action,
                        self.patient_name,
                        self.dob,
                        self.gender,
                        self.nationality,
                        self.diagnosis,
                        self.floor_unit,
                        self.room,
                        self.supervisor_email,
                        1 if self.good_catch_event else 0,
                        1 if self.pending else 0,
                        self.type_of_error,
                        self.recommended_action_plan,
                        self.action_plan_others,
                        self.supervisor_comments,
                        self.department_unit_involved,
                        self.department_unit_involved_2,
                        self.initial_scoring,
                        1 if self.is_bmt_patient else 0,
                        self.bmt_physician_name,
                        self.bmt_occurrence_category,
                        self.bmt_patient_donor_notified,
                        self.bmt_patient_donor_notified_time,
                        self.bmt_ctag_reviewed,
                        self.bmt_ctag_reviewed_time,
                        self.bmt_program_director_notified,
                        self.bmt_program_director_time,
                        self.bmt_program_director_date,
                        self.bmt_attending_notified,
                        self.bmt_attending_time,
                        self.bmt_attending_date,
                        self.bmt_quality_council_date,
                        self.bmt_comments
                    ]
                    
                    cursor.execute(sql, params)
                    # Get the newly created event_number
                    self.event_number = cursor.fetchone()[0]
                    print(f"Created new event with event_number: {self.event_number}")

                print("Successfully saved event")
                
        except Exception as e:
            print(f"Error saving event: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

class EventNote(models.Model):
    note_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE,
        db_column='event_number'
    )
    note_text = models.TextField()
    user_email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '[datahub].[Event_Notes]'
        managed = False

class ModificationLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE,
        db_column='event_number'
    )
    modified_by = models.EmailField()
    modification_type = models.CharField(max_length=50)  # Update, Delete, etc.
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(null=True)
    new_value = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '[datahub].[Event_Modification_Logs]'
        managed = False
        ordering = ['-timestamp']

class EventAssignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE,
        db_column='event_number'
    )
    user_email = models.EmailField()
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '[datahub].[Event_Assignments]'
        managed = False

class EventComment(models.Model):
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='comments',
        db_column='event_number'
    )
    comment = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = '[datahub].[Event_Comments]'
        managed = False

    def __str__(self):
        return f'Comment by {self.created_by.username} on {self.event}'
    
class EventCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE,
        db_column='event_number',
        related_name='categories'
    )
    category_type = models.CharField(max_length=50)
    subcategory = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '[datahub].[Event_Categories]'
        managed = False