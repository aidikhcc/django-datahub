from django import forms
from .models import (
    BreastKPI, Physicians,
    GENDER_CHOICES, NATIONALITY_CHOICES, CPG_CHOICES,
    TREATMENT_TYPE_CHOICES, DELAY_REASON_CHOICES,
    SCREENING_INVESTIGATION_CHOICES, YES_NO_CHOICES,
    RADIO_DELAY_CHOICES, CPG_NO_CHOICES, CPG_SPECIAL_CAUSE_CHOICES
)

class BreastKPIForm(forms.ModelForm):
    # Define physician fields as ChoiceFields
    Oncologist_name = forms.ChoiceField(
        choices=[('', '---------')],  # Will be populated in __init__
        widget=forms.Select(attrs={
            'class': 'form-select select2',
            'placeholder': 'Select Oncologist'
        }),
        required=False
    )
    
    Surgeon_name = forms.ChoiceField(
        choices=[('', '---------')],  # Will be populated in __init__
        widget=forms.Select(attrs={
            'class': 'form-select select2',
            'placeholder': 'Select Surgeon'
        }),
        required=False
    )
    
    Radiotherapist_name = forms.ChoiceField(
        choices=[('', '---------')],  # Will be populated in __init__
        widget=forms.Select(attrs={
            'class': 'form-select select2',
            'placeholder': 'Select Radiotherapist'
        }),
        required=False
    )

    class Meta:
        model = BreastKPI
        fields = '__all__'
        widgets = {
            # Text and Number inputs
            'MRN': forms.TextInput(attrs={'class': 'form-control'}),
            'Age': forms.NumberInput(attrs={'class': 'form-control'}),
            
            # Date inputs
            'Screening_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Insurance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'MDT_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Treatment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Neoadjuvant_ctx_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Surgery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'surgery_last_dose_adjuvant_chemotherapy_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Radio_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Last_Follow_up_Date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Next_Follow_up_Date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            # Select inputs with choices
            'Gender': forms.Select(attrs={'class': 'form-select select2'}),
            'Nationality': forms.Select(attrs={'class': 'form-select select2'}),
            'Patient_on_CPG': forms.Select(attrs={'class': 'form-select select2', 'onchange': 'toggleCPGFields(this.value)'}),
            'Treatment_type': forms.Select(attrs={
                'class': 'form-select select2'
            }, choices=TREATMENT_TYPE_CHOICES),
            'Reason_for_the_delay': forms.Select(attrs={
                'class': 'form-select select2'
            }, choices=DELAY_REASON_CHOICES),
            'Need_more_screening_investigation': forms.Select(attrs={
                'class': 'form-select select2'
            }, choices=SCREENING_INVESTIGATION_CHOICES),
            'Neoadju_Bfr_Surgery': forms.Select(attrs={'class': 'form-select select2'}),
            'Adjuvant_radiotherapy': forms.Select(attrs={'class': 'form-select select2'}),
            'Rdio_delay_why': forms.Select(attrs={
                'class': 'form-select select2'
            }, choices=RADIO_DELAY_CHOICES),
            'CPG_No': forms.Select(attrs={
                'class': 'form-select select2'
            }, choices=CPG_NO_CHOICES),
            'CPG_Special_cause': forms.Select(attrs={
                'class': 'form-select select2'
            }, choices=CPG_SPECIAL_CAUSE_CHOICES),
            
            # CNC name as text input
            'CNC_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter CNC Name'
            }),
            
            # Toggle switches
            'Treatment_NotFitForThisKPI': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
                'data-toggle': 'toggle',
                'data-on': 'Yes',
                'data-off': 'No',
                'data-onstyle': 'primary',
                'data-offstyle': 'light'
            }),
            'Surgery_NotFitForThisKPI': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
                'data-toggle': 'toggle',
                'data-on': 'Yes',
                'data-off': 'No',
                'data-onstyle': 'primary',
                'data-offstyle': 'light'
            }),
            'Radio_NotFitForThisKPI': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
                'data-toggle': 'toggle',
                'data-on': 'Yes',
                'data-off': 'No',
                'data-onstyle': 'primary',
                'data-offstyle': 'light'
            }),
            'Pending': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
                'data-toggle': 'toggle',
                'data-on': 'Yes',
                'data-off': 'No',
                'data-onstyle': 'primary',
                'data-offstyle': 'light'
            }),
            
            # Textareas
            'Surgeryneo_Delay_why': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter reason for delay...'
            }),
            'Followup_remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter follow-up remarks...'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Extract user from kwargs before calling super
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set default CNC name for new instances
        if user and user.is_authenticated and not self.instance.pk:  # Only for new instances with authenticated users
            default_cnc_name = f"{user.first_name} {user.last_name}".strip()
            if default_cnc_name:
                self.initial['CNC_name'] = default_cnc_name
        
        # Initialize physician fields with choices from database
        try:
            # Query the physicians once
            oncologists = Physicians.objects.filter(Disease='Breast', Physician_type='Oncologist')
            surgeons = Physicians.objects.filter(Disease='Breast', Physician_type='Surgeon')
            radiotherapists = Physicians.objects.filter(Disease='Breast', Physician_type='Radiotherapist')
            
            # Set the choices
            self.fields['Oncologist_name'].choices = [('', '---------')] + [
                (doc.Physician_name, doc.Physician_name) 
                for doc in oncologists
            ]
            self.fields['Surgeon_name'].choices = [('', '---------')] + [
                (doc.Physician_name, doc.Physician_name) 
                for doc in surgeons
            ]
            self.fields['Radiotherapist_name'].choices = [('', '---------')] + [
                (doc.Physician_name, doc.Physician_name) 
                for doc in radiotherapists
            ]
            
        except Exception as e:
            print(f"Error setting up physician choices: {str(e)}")
        
        # Make all fields not required initially
        for field in self.fields:
            self.fields[field].required = False
            
            # Add placeholder text for text inputs
            if isinstance(self.fields[field].widget, forms.TextInput):
                self.fields[field].widget.attrs['placeholder'] = f'Enter {field.replace("_", " ").title()}'
            
            # Add placeholder text for date inputs
            if isinstance(self.fields[field].widget, forms.DateInput):
                self.fields[field].widget.attrs['placeholder'] = f'Select {field.replace("_", " ").title()}'
        
        # Set choices for CPG fields
        self.fields['CPG_No'].choices = CPG_NO_CHOICES
        self.fields['CPG_Special_cause'].choices = CPG_SPECIAL_CAUSE_CHOICES
        
        # Add JavaScript to handle CPG field dependencies
        self.fields['Patient_on_CPG'].widget.attrs['onchange'] = 'toggleCPGFields(this.value)'
        
        # Initially disable both fields
        self.fields['CPG_No'].widget.attrs['disabled'] = True
        self.fields['CPG_Special_cause'].widget.attrs['disabled'] = True
        
        # Enable appropriate field based on Patient_on_CPG value
        if self.instance.Patient_on_CPG == 'No':
            self.fields['CPG_No'].widget.attrs['disabled'] = False
        elif self.instance.Patient_on_CPG == 'Special cause':
            self.fields['CPG_Special_cause'].widget.attrs['disabled'] = False
        