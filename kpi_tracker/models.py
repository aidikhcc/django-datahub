from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.models import UserManager

# Add choices at the top level
GENDER_CHOICES = [
    ('', '----'),
    ('Male', 'Male'),
    ('Female', 'Female')
]

NATIONALITY_CHOICES = [
    ('', '----'),
    ('Jordanian', 'Jordanian'),
    ('Non Jordanian', 'Non Jordanian')
]

CPG_CHOICES = [
    ('', '----'),
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('Special cause', 'Special cause')
]

TREATMENT_TYPE_CHOICES = [
    ('', '---------'),
    ('NeoAdjuvant CTx', 'NeoAdjuvant CTx'),
    ('Adjuvant CTx', 'Adjuvant CTx'),
    ('Surgery', 'Surgery'),
    ('Chemotherapy', 'Chemotherapy'),
    ('Chemo-radiotherapy', 'Chemo-radiotherapy'),
    ('Radiotherapy', 'Radiotherapy'),
    ('Hormonal', 'Hormonal'),
    ('Palliative', 'Palliative'),
    ('Palliative chemotherapy', 'Palliative chemotherapy'),
    ('None', 'None')
]

DELAY_REASON_CHOICES = [
    ('', '---------'),
    ('Not fit for starting treatment', 'Not fit for starting treatment'),
    ('Need more screening investigation', 'Need more screening investigation'),
    ('Pathology delay', 'Pathology delay'),
    ('Admission list', 'Admission list'),
    ('Radiotherapy list', 'Radiotherapy list'),
    ('Chemotherapy list', 'Chemotherapy list'),
    ('Surgery list', 'Surgery list'),
    ('Financial issues', 'Financial issues'),
    ('COVID issues', 'COVID issues'),
    ('Miss her appointment', 'Miss her appointment'),
    ('Need more time to think', 'Need more time to think'),
    ('Patient related', 'Patient related'),
    ('Delay on referral or clearance to other non-oncology services clinic', 'Delay on referral or clearance'),
    ('Delay on referral to other oncology services', 'Delay on referral to oncology'),
    ('Missed follow up from clinic', 'Missed follow up from clinic'),
    ('Patient ready and not discussed in MDC', 'Patient ready and not discussed in MDC')
]

SCREENING_INVESTIGATION_CHOICES = [
    ('', '---------'),
    ('2nd look scan', '2nd look scan'),
    ('Need another scan', 'Need another scan'),
    ('Need biopsy', 'Need biopsy'),
    ('Need Echo', 'Need Echo'),
    ('Genetic test delay', 'Genetic test delay'),
    ('Fertility issues', 'Fertility issues'),
    ('More consultations', 'More consultations'),
    ('Endocrine clearance', 'Endocrine clearance'),
    ('Pulmonary clearance', 'Pulmonary clearance'),
    ('Abnormal laboratory findings', 'Abnormal laboratory findings'),
    ('Tumor marker processing time', 'Tumor marker processing time')
]

YES_NO_CHOICES = [
    ('', '----'),
    ('Yes', 'Yes'),
    ('No', 'No')
]

RADIO_DELAY_CHOICES = [
    ('', '---------'),
    ('Not fit to start radiotherapy', 'Not fit to start radiotherapy'),
    ('Patient related', 'Patient related'),
    ('Clinic appointment list', 'Clinic appointment list'),
    ('Miss her appointment', 'Miss her appointment'),
    ('COVID issues', 'COVID issues'),
    ('Review pathology report', 'Review pathology report'),
    ('Radiotherapy list', 'Radiotherapy list'),
    ('Need more time to think', 'Need more time to think'),
    ('Surgical issues', 'Surgical issues'),
    ('Insurance issues', 'Insurance issues'),
    ('Cardio clearance', 'Cardio clearance'),
    ('Delay in referral', 'Delay in referral'),
    ('Need more investigation', 'Need more investigation'),
    ('Patient refuse', 'Patient refuse')
]

CPG_NO_CHOICES = [
    ('', '---------'),
    ('Palliative', 'Palliative'),
    ('Patient refused treatment plan', 'Patient refused treatment plan'),
    ('Patient was started out KHCC non-standardized treatment protocol & can\'t continue as KHCC guidelines', 
     'Patient was started out KHCC non-standardized treatment protocol & can\'t continue as KHCC guidelines')
]

CPG_SPECIAL_CAUSE_CHOICES = [
    ('', '---------'),
    ('Benign', 'Benign'),
    ('No show before treatment', 'No show before treatment'),
    ('Death before treatment', 'Death before treatment'),
    ('Second opinion', 'Second opinion'),
    ('Referred for specific treatment', 'Referred for specific treatment')
]

class CustomUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset()

class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    last_login = models.DateTimeField(null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    azure_id = models.CharField(max_length=255, unique=True, null=True)
    email = models.CharField(max_length=254, unique=True)
    
    password = None
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='kpi_tracker_users',
        blank=True,
        through='UserGroups',
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='kpi_tracker_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    REQUIRED_FIELDS = ['email']
    
    objects = CustomUserManager()
    
    class Meta:
        db_table = '[datahub].[KPI_Users]'
        managed = False
        app_label = 'kpi_tracker'
        permissions = [
            ("view_breast_kpi", "Can view Breast Cancer KPIs"),
            ("edit_breast_kpi", "Can edit Breast Cancer KPIs"),
            ("view_analytics", "Can view Analytics"),
            ("admin_access", "Has admin access"),
            ("view_qmo_dashboard", "Can view QMO Dashboard"),
            ("view_all_events", "Can view all events"),
            ("manage_events", "Can manage events"),
            ("export_reports", "Can export reports"),
        ]
    
    def __str__(self):
        return self.email

    def get_group_ids(self):
        return User.objects.raw("""
            SELECT u.id, ug.group_id
            FROM [datahub].[KPI_Users] u
            LEFT JOIN [datahub].[KPI_Users_Groups] ug ON u.id = ug.user_id
            LEFT JOIN [auth_group] g ON ug.group_id = g.id
            WHERE u.id = %s
        """, [self.id])

    def set_password(self, raw_password):
        pass

    def check_password(self, raw_password):
        return False

    def save(self, *args, **kwargs):
        self._password = None
        super().save(*args, **kwargs)

    @property
    def backend(self):
        return 'microsoft_auth.backends.MicrosoftAuthenticationBackend'
    
    def has_usable_password(self):
        return False

class UserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        db_table = '[datahub].[KPI_Users_Groups]'
        managed = False
        unique_together = ('user', 'group')

class BreastKPI(models.Model):
    MRN = models.CharField(max_length=50, primary_key=True)
    CNC_name = models.CharField(max_length=100, blank=True, null=True)
    Screening_date = models.DateField(null=True, blank=True)
    Insurance_date = models.DateField(null=True, blank=True)
    Gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    Age = models.IntegerField(null=True, blank=True)
    Nationality = models.CharField(max_length=20, choices=NATIONALITY_CHOICES, blank=True, null=True)
    Patient_on_CPG = models.CharField(max_length=20, choices=CPG_CHOICES, blank=True, null=True)
    CPG_No = models.CharField(max_length=200, choices=CPG_NO_CHOICES, blank=True, null=True)
    CPG_Special_cause = models.CharField(max_length=100, choices=CPG_SPECIAL_CAUSE_CHOICES, blank=True, null=True)
    MDT_date = models.DateField(null=True, blank=True)
    Treatment_date = models.DateField(null=True, blank=True)
    Treatment_type = models.CharField(max_length=50, choices=TREATMENT_TYPE_CHOICES, blank=True, null=True)
    Reason_for_the_delay = models.CharField(max_length=100, choices=DELAY_REASON_CHOICES, blank=True, null=True)
    Need_more_screening_investigation = models.CharField(max_length=100, choices=SCREENING_INVESTIGATION_CHOICES, blank=True, null=True)
    Treatment_NotFitForThisKPI = models.BooleanField(default=False)
    Neoadju_Bfr_Surgery = models.CharField(max_length=3, choices=YES_NO_CHOICES, blank=True, null=True)
    Neoadjuvant_ctx_date = models.DateField(null=True, blank=True)
    Surgery_date = models.DateField(null=True, blank=True)
    Surgeryneo_Delay_why = models.TextField(blank=True, null=True)
    Surgery_NotFitForThisKPI = models.BooleanField(default=False)
    Adjuvant_radiotherapy = models.CharField(max_length=3, choices=YES_NO_CHOICES, blank=True, null=True)
    surgery_last_dose_adjuvant_chemotherapy_date = models.DateField(null=True, blank=True)
    Radio_date = models.DateField(null=True, blank=True)
    Rdio_delay_why = models.CharField(max_length=100, choices=RADIO_DELAY_CHOICES, blank=True, null=True)
    Radio_NotFitForThisKPI = models.BooleanField(default=False)
    Pending = models.BooleanField(default=True)
    Oncologist_name = models.CharField(max_length=100, blank=True, null=True)
    Surgeon_name = models.CharField(max_length=100, blank=True, null=True)
    Radiotherapist_name = models.CharField(max_length=100, blank=True, null=True)
    entry_ts = models.DateTimeField(auto_now_add=True)
    last_update_ts = models.DateTimeField(auto_now=True)
    Last_Follow_up_Date = models.DateField(null=True, blank=True)
    Next_Follow_up_Date = models.DateField(null=True, blank=True)
    Followup_remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = '[datahub].[KPI_TblBreast]'
        managed = False

class KPIActivityLog(models.Model):
    log_id = models.BigIntegerField(primary_key=True)
    SourcePage = models.CharField(max_length=50)
    UserName = models.CharField(max_length=100)
    UserEmail = models.CharField(max_length=100)
    UserID = models.CharField(max_length=100)
    MRN = models.CharField(max_length=50)
    ts = models.DateTimeField()
    Type = models.CharField(max_length=50)
    Pending_Status = models.BooleanField()

    class Meta:
        db_table = '[datahub].[KPI_ActivityLog]'
        managed = False

class Physicians(models.Model):
    Disease = models.CharField(max_length=50)
    Physician_type = models.CharField(max_length=50)
    Physician_name = models.CharField(max_length=100)

    class Meta:
        db_table = '[datahub].[KPI_TblPhysicians]'
        managed = False