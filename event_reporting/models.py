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

    class Meta:
        db_table = '[datahub].[Event_Reports]'
        managed = False

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