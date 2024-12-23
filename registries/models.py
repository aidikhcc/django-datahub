from django.db import models
from django.contrib.auth.models import User

class BMTRegistry(models.Model):
    MRN = models.CharField(max_length=50)
    patient_name = models.CharField(max_length=255, db_column='Patient_name')
    physician_name = models.CharField(max_length=255, db_column='Physician_name')
    birth_date = models.DateField(db_column='Birth_date')
    gender = models.CharField(max_length=10, db_column='Gender')
    transplant_number = models.CharField(max_length=20, db_column='Number_of_Transplant')
    initial_diagnosis_date = models.DateField(db_column='Initial_Diagnosis_date')
    age = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        db_column='Age'
    )
    nationality = models.CharField(max_length=100, db_column='Nationality')
    transplant_date = models.DateField(db_column='Transplant_Date')
    service = models.CharField(max_length=50, db_column='Service')
    diagnosis = models.CharField(max_length=255, db_column='Diagnosis')
    disease_classification = models.CharField(max_length=255, db_column='Disease_Classification_Status_Pre_Transplantation')
    disease_classification_detail = models.TextField(null=True, blank=True, db_column='Disease_Classification_Status_Pre_Transplantation_Detail')
    patient_blood_group = models.CharField(max_length=50, db_column='Patient_Blood_Group')
    disease_category = models.CharField(max_length=100, db_column='Disease_Category')
    malignant_status = models.CharField(max_length=50, db_column='Malignant_vs_Non_Malignant')
    performance_status = models.CharField(max_length=255, db_column='Performance_status')
    previous_malignancies = models.TextField(null=True, blank=True, db_column='Previous_malignancies')
    patient_cmv_status = models.CharField(max_length=50, db_column='Patient_CMV_status')
    
    # Transplant Information
    admission_date = models.DateField(db_column='Admission_Date')
    conditioning_start_date = models.DateField(db_column='Conditioning_Start_date')
    donor_type = models.CharField(max_length=50, db_column='Donor_Type')
    transplant_type = models.CharField(max_length=50, db_column='Type_of_Transplant')
    stem_cell_source = models.CharField(max_length=50, db_column='Stem_Cell_Source')
    conditioning_intensity = models.CharField(max_length=50, db_column='Conditioning_Intensity')
    conditioning_regimen = models.CharField(max_length=255, db_column='Conditioning_Regimen')
    gvhd_prophylaxis = models.CharField(max_length=255, db_column='GVHD_Prophylaxis')
    cd34_positive = models.FloatField(null=True, blank=True, db_column='CD34_positive')

    # Donor Information
    donor_id = models.CharField(max_length=50, null=True, blank=True, db_column='Donor_ID')
    donor_relation = models.CharField(max_length=50, null=True, blank=True, db_column='Donor_Relation')
    donor_age = models.FloatField(null=True, blank=True, db_column='Donor_Age')
    donor_gender = models.CharField(max_length=10, null=True, blank=True, db_column='Donor_Gender')
    donor_blood_group = models.CharField(max_length=50, null=True, blank=True, db_column='Donor_Blood_Group')
    donor_cmv_status = models.CharField(max_length=50, null=True, blank=True, db_column='Donor_CMV_status')
    donor_birth_date = models.DateField(null=True, blank=True, db_column='Donor_BirthDate')
    hla = models.CharField(max_length=50, null=True, blank=True, db_column='HLA')
    dr_sex_match = models.CharField(max_length=50, null=True, blank=True, db_column='DR_Sex_Match')

    # Engraftment Information
    neutrophil_engraftment = models.CharField(max_length=50, null=True, blank=True, db_column='Neutrophil_Engraftment')
    platelets_engraftment = models.CharField(max_length=50, null=True, blank=True, db_column='Platelets_Engraftment')
    neutrophil_engraftment_date = models.DateField(null=True, blank=True, db_column='Neutrophil_Engraftment_Date')
    platelets_engraftment_date = models.DateField(null=True, blank=True, db_column='Platelets_Engraftment_Date')
    neutrophil_engraftment_days = models.IntegerField(null=True, blank=True, db_column='Neutrophil_Engraftment_Days_post_BMT')
    platelets_engraftment_days = models.IntegerField(null=True, blank=True, db_column='Platelets_Engraftment_Days_post_BMT')

    # GVHD Information
    acute_gvhd_date = models.DateField(null=True, blank=True, db_column='Acute_GVHD_Diagnosis_Date')
    acute_gvhd = models.CharField(max_length=10, null=True, blank=True, db_column='Acute_GVHD')
    acute_gvhd_grade = models.CharField(max_length=50, null=True, blank=True, db_column='Acute_GVHD_grade')
    acute_gvhd_skin = models.CharField(max_length=50, null=True, blank=True, db_column='Acute_GVHD_Skin_stage')
    acute_gvhd_gut = models.CharField(max_length=50, null=True, blank=True, db_column='Acute_GVHD_Gut_stage')
    acute_gvhd_liver = models.CharField(max_length=50, null=True, blank=True, db_column='Acute_GVHD_liver_stage')
    
    chronic_gvhd_date = models.DateField(null=True, blank=True, db_column='CGVHD_diagnosis_Date')
    chronic_gvhd = models.CharField(max_length=10, null=True, blank=True, db_column='CGVHD')
    chronic_gvhd_severity = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_Overall_severity')
    chronic_gvhd_skin = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_skin')
    chronic_gvhd_mouth = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_mouth')
    chronic_gvhd_eyes = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_eyes')
    chronic_gvhd_gi = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_GI')
    chronic_gvhd_liver = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_liver')
    chronic_gvhd_lungs = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_lungs')
    chronic_gvhd_joints = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_Joints_and_fascia')
    chronic_gvhd_genital = models.CharField(max_length=50, null=True, blank=True, db_column='CGVHD_Genital_tract')

    # Follow-up Information
    discharge_date = models.DateField(null=True, blank=True, db_column='Discharge_Date')
    relapse_date = models.DateField(null=True, blank=True, db_column='Relapse_Date')
    death_date = models.DateField(null=True, blank=True, db_column='Death_Date')
    last_followup_date = models.DateField(null=True, blank=True, db_column='Last_Follow_up_date')
    last_visit_date = models.DateField(null=True, blank=True, db_column='Last_Visit_Date')
    hospitalization_days = models.IntegerField(null=True, blank=True, db_column='Hospitalization_Duration_Days')
    icu_admission_100d = models.CharField(max_length=10, null=True, blank=True, db_column='ICU_Admission_within_100_day_post_BMT')
    disease_status = models.CharField(max_length=50, null=True, blank=True, db_column='Disease_Status_at_last_follow_up')
    relapse_days = models.IntegerField(null=True, blank=True, db_column='relapse_day_post_bmt')
    relapse_site = models.CharField(max_length=255, null=True, blank=True, db_column='Relapse_site')
    patient_status = models.CharField(max_length=50, null=True, blank=True, db_column='Patient_Status')
    ebmt_notes = models.TextField(null=True, blank=True, db_column='EBMT_Notes')
    days_since_transplant = models.IntegerField(null=True, blank=True, db_column='Days_Since_Transplant')
    cause_of_death = models.TextField(null=True, blank=True, db_column='Cause_of_Death')
    transplant_related_cause = models.CharField(max_length=50, null=True, blank=True, db_column='Transplant_Related_Cause')
    
    # Follow-up tracking
    followup_done = models.BooleanField(default=False, db_column='Follow_up_Done')
    followup_type = models.CharField(max_length=50, null=True, blank=True, db_column='Type_of_follow_up_report')
    followup_remarks = models.TextField(null=True, blank=True, db_column='Remarks_Last_Date_of_Followup')
    next_followup_date = models.DateField(null=True, blank=True, db_column='Next_Follow_up_Due_Date')
    next_followup_type = models.CharField(max_length=50, null=True, blank=True, db_column='Type_of_Next_Follow_up_report')
    lost_to_followup = models.BooleanField(default=False, db_column='lost_to_follow_up')

    # Timestamps
    entry_ts = models.DateTimeField(auto_now_add=True, db_column='entry_ts')
    last_update_ts = models.DateTimeField(auto_now=True, db_column='last_update_ts')

    class Meta:
        app_label = 'registries'
        db_table = '[datahub].[Registry_BMT]'
        managed = False
        unique_together = ('MRN', 'transplant_number')

    def __str__(self):
        return f"{self.MRN} - {self.transplant_number}"

class BMTActivityLog(models.Model):
    log_id = models.BigIntegerField(primary_key=True)
    source_page = models.CharField(max_length=255, db_column='SourcePage')
    username = models.CharField(max_length=255, db_column='UserName')
    user_email = models.CharField(max_length=255, db_column='UserEmail')
    user_id = models.CharField(max_length=255, db_column='UserID')
    mrn = models.CharField(max_length=50, db_column='MRN')
    timestamp = models.DateTimeField(db_column='ts')
    action_type = models.CharField(max_length=50, db_column='Type')
    pending_status = models.CharField(max_length=10, db_column='Pending_Status')
    value_string = models.TextField(db_column='valuestring')

    class Meta:
        app_label = 'registries'
        db_table = '[datahub].[KPI_ActivityLog]'
        managed = False
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.mrn} - {self.action_type} by {self.username}" 