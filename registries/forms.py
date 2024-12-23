from django import forms
from .models import BMTRegistry
from django.core.exceptions import ValidationError
from django.utils import timezone

# Constants from Streamlit
DIAGNOSIS_OPTIONS = [
    "ALL", "AML", "NHL", "HD", "Germ Cell Tumor", "JMML", "CML", "Neuroblastoma", 
    "Fanconi Anemia", "Thalassemia", "Renal Cell Carcinoma", "SCID", "Griscelli Syndrome",
    "Multiple Myeloma", "Osteopetrosis", "Aplastic Anemia", "Gaucher Disease", "MDS",
    "Myelofibrosis", "Ewing Sarcoma", "Synovial Cell Sarcoma", "Mucopolysaccharidosis (type VI)",
    "Wiskott-Aldrich Syndrome", "DiGeorge Syndrome", "Sickle Cell Anemia", "Omenn's Syndrome",
    "Chediak Higashi", "Red Cell Aplasia", "PNET", "Metachromatic Leukodestrophy",
    "Leukemia (N-K Lymphocytosis)", "Hemophagocytic Lympho Histocytosis", "APL",
    "Autoimmune lymphoproliferative Syndrome", "Amegakaryocytic Thrombocytopenia",
    "Medulloblastoma", "Wilm's Tumor", "Hypogammaglobulinemia", "Retinoblastoma",
    "Chronic Granulomatous Disease", "ATRT", "Plasmacytoma", "Meningeal Sarcoma",
    "Biphenotypic Leukemia", "Leukocyte Adhesion Deficiency", "Choroid Plexus Carcinoma",
    "C-ALD", "Composite HL/NHL", "CMML", "Severe Congenital Neutropenia", "Kostmann Syndrome",
    "Sideroblastic Anemia", "CID", "ALPS", "Hemolytic anemia", "Kidney Clear Cell Sarcoma",
    "Amyloidosis", "Dyskeratosis Congenita", "Hyper IgM Syndrome", "Poems Syndrome",
    "Histiocytic Sarcoma", "Mucopolysaccharidosis (type II)", "Adrenoleukodystrophy",
    "Hyper IgE Syndrome", "Pineal Embryonal Tumor", "CLL/SLL", "Congenital Neutropenia",
    "Mucopolysaccharidosis (type IVA)", "ETMR", "Paroxysmal Nocturnal Haemoglobinuria",
    "Supratentorial Embryonal Tumour", "Neuroblastoma (Renal)", "NK/T-cell Lymphoma",
    "Congenital Bone Marrow Failure Syndrome", "BPDCN", "Pineoblastoma",
    "Langerhans Cell Histiocytosis", "Mucopolysaccharidosis (type I)",
    "GALE mutation (Panctopenia)", "Severe T-cell Difficiency", "MHC class II deficiency"
]

NATIONALITY_MAP = {
    "JOR": "Jordanian",
    "PAL": "Palestinian",
    "SYR": "Syrian",
    "IRQ": "Iraqi",
    "YEM": "Yemeni",
    "LBY": "Libyan",
    "SDN": "Sudanese",
    # Add other nationalities as needed
}

PERFORMANCE_STATUS_OPTIONS = [
    ("100", "100: Normal no complaints no evidence of disease."),
    ("90", "90: Able to carry on normal activity minor signs or symptoms of disease."),
    ("80", "80: Normal activity with effort; some signs or symptoms of disease."),
    ("70", "70: Cares for self; unable to carry on normal activity or to do active work."),
    ("60", "60: Requires occasional assistance, but is able to care for most of his personal needs"),
    ("50", "50: Requires considerable assistance and frequent medical care"),
    ("40", "40: Disabled; requires special care and assistance."),
    ("30", "30: Severely disabled; hospital admission is indicated although death not imminent."),
    ("20", "20: Very sick; hospital admission necessary; active supportive treatment necessary."),
    ("10", "10: Moribund; fatal processes progressing rapidly."),
    ("0", "0: Dead")
]

CONDITIONING_REGIMEN_OPTIONS = [
    "Cy/TBI", "Bu/Cy", "BEAM", "Carbo/Etop/Ifos", "Bu/Cy/Etop", "Cy/Flu", "Bu/Mel",
    "Flu/TBI", "Carbo/Etop/Mel", "Melphalan", "Flu/Mel", "Mel/TBI", "Bu/Etop/Flu",
    "Bu/Flu/Thio", "Flu", "Bu/Flu/TLI", "Cy", "Bu/Flu", "Carbo/Cy/Ifos", "Bu/Cy/Flu",
    "Cy/Thio/TBI", "Carbo/Etop/Thio", "Cy/Flu/TBI", "Carbo/Etop", "TEAM", "Bu/Cy/Mel",
    "Cy/Flu/TLI", "Flu/Treosulfan", "Cy/Flu/Thio/TBI", "Carbo/Mel/Thio", "Bu/Thio",
    "Flu/Mel/TBI", "Etop/Flu/Mel", "BCNU/Etop/Thio", "Flu/Mel/Thio", "Flu/Thio/TBI",
    "Bu/Flu/Thio/TLI", "Campath/Flu/Mel", "Flu/Rituximab", "Campath/Flu/Mel/Thio/TBI",
    "Capmath/Bu/Flu/TLI", "BCNU/Thio", "Bu/Flu/Mel", "Bu/Cy/Rituximab", 
    "Bu/Cy/Flu/Thio/TBI", "Bu/Flu/Rituximab/Thio", "Flu/Mel/Thiotepa", "LACE",
    "Flu/Rituximab/Thio/TBI", "Flu/Bu", "BCNU/VP-16/THIOTEPA"
]

GVHD_PROPHYLAXIS_OPTIONS = [
    "CSA/MTX", "tacrolimus/MMF", "Unknown", "CSA/MMF", "ATG/CSA/MTX", "tacrolimus/MTX",
    "ATG/CSA/MMF", "CSA", "ATG", "ATG/tacrolimus/MMF", "MTX/Campath in bag",
    "ATG/Tacrolimus/MTX", "CSA/Campath-in", "ATG/CSA/MMF/Campath in bag",
    "tacrolimus/MMF/Cy", "CSA/MMF/Cy", "CSA/MTX/Cy", "tacrolimus/alpha-beta depleted",
    "NO GVHD Prophylaxis (as alpha and beta T-cell is zero)", "alpha beta depletion/CSA",
    "ATG/Prograf/MMF/Cy"
]

class BMTSearchForm(forms.Form):
    mrn = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter MRN'
        })
    )
    transplant_number = forms.ChoiceField(
        choices=[('', '-- Select --')] + [
            ('1st Transplant', '1st Transplant'),
            ('2nd Transplant', '2nd Transplant'),
            ('3rd Transplant', '3rd Transplant'),
            ('4th Transplant', '4th Transplant'),
            ('5th Transplant', '5th Transplant')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class BMTRegistryForm(forms.ModelForm):
    class Meta:
        model = BMTRegistry
        exclude = ['entry_ts', 'last_update_ts', 'MRN', 'transplant_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Common styling for all fields
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

        # Update age field widget
        self.fields['age'].widget = forms.NumberInput(
            attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '120',
                'placeholder': 'Enter age'
            }
        )

        empty_choice = [('', '-- Select --')]

        # Basic dropdowns
        self.fields['gender'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=[('', '-- Select --'), ('Male', 'Male'), ('Female', 'Female')]
        )
        
        self.fields['nationality'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [(k, v) for k, v in NATIONALITY_MAP.items()]
        )

        self.fields['service'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [
                ('Adult Service', 'Adult Service'),
                ('Pediatric Service', 'Pediatric Service')
            ]
        )

        # Physician Name dropdown
        physician_names = [
            "Khalid Halahleh", "Husam Abu-Jazar", "Mohammad Makoseh", 
            "Zaid Abdel Rahman", "Salwa Saadeh", "Waleed Dana", 
            "Rozan Al-Far", "Rawad Rihani", "Hasan Hashem", 
            "Mayada Abu Shanap", "Eman Khattab", "Dauaa Zandaki"
        ]
        self.fields['physician_name'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [(name, name) for name in sorted(physician_names)]
        )

        # Disease Information dropdowns
        self.fields['diagnosis'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [(d, d) for d in DIAGNOSIS_OPTIONS]
        )

        self.fields['disease_classification'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [
                ('CR', 'CR'), ('CR1', 'CR1'), ('CR2', 'CR2'),
                ('PR', 'PR'), ('PR1', 'PR1'), ('PR2', 'PR2'),
                ('VGPR', 'VGPR'), ('Stable', 'Stable'), ('Progressive', 'Progressive')
            ]
        )

        self.fields['disease_status'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [
                ('Relapse', 'Relapse'),
                ('Remission', 'Remission'),
                ('Mixed chimerism', 'Mixed chimerism'),
                ('Unknown', 'Unknown')
            ]
        )

        self.fields['malignant_status'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [
                ('Malignant', 'Malignant'),
                ('Non-Malignant', 'Non-Malignant')
            ]
        )

        # Blood Group choices
        blood_group_choices = empty_choice + [
            ('A Negative', 'A Negative'), ('A Positive', 'A Positive'),
            ('A2 Negative', 'A2 Negative'), ('A2 Positive', 'A2 Positive'),
            ('A2B Negative', 'A2B Negative'), ('A2B Positive', 'A2B Positive'),
            ('AB Negative', 'AB Negative'), ('AB Positive', 'AB Positive'),
            ('B Negative', 'B Negative'), ('B Positive', 'B Positive'),
            ('O Negative', 'O Negative'), ('O Positive', 'O Positive')
        ]
        self.fields['patient_blood_group'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=blood_group_choices
        )
        self.fields['donor_blood_group'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=blood_group_choices
        )

        # CMV Status choices
        cmv_choices = empty_choice + [
            ('Positive', 'Positive'),
            ('Negative', 'Negative'),
            ('Other/Unknown', 'Other/Unknown')
        ]
        self.fields['patient_cmv_status'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=cmv_choices
        )
        self.fields['donor_cmv_status'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=cmv_choices
        )

        # Performance Status
        self.fields['performance_status'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + PERFORMANCE_STATUS_OPTIONS
        )

        # Conditioning Regimen
        self.fields['conditioning_regimen'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [(reg, reg) for reg in CONDITIONING_REGIMEN_OPTIONS]
        )

        # GVHD Prophylaxis
        self.fields['gvhd_prophylaxis'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [(opt, opt) for opt in GVHD_PROPHYLAXIS_OPTIONS]
        )

        # Donor Type choices
        donor_type_choices = [
            ('MRD', 'Matched Related Donor (MRD)'),
            ('MMRD', 'Mismatched Related Donor (MMRD)'),
            ('MUD', 'Matched Unrelated Donor (MUD)'),
            ('MMUD', 'Mismatched Unrelated Donor (MMUD)'),
            ('Haplo', 'Haploidentical'),
            ('Cord', 'Cord Blood')
        ]
        self.fields['donor_type'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + donor_type_choices
        )

        # Stem Cell Source
        self.fields['stem_cell_source'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [
                ('BM', 'Bone Marrow'),
                ('PBSC', 'Peripheral Blood Stem Cells'),
                ('Cord', 'Cord Blood')
            ]
        )

        # Conditioning Intensity
        self.fields['conditioning_intensity'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [
                ('MAC', 'Myeloablative'),
                ('RIC', 'Reduced Intensity'),
                ('NMA', 'Non-Myeloablative')
            ]
        )

        # Patient Status
        self.fields['patient_status'].widget = forms.Select(
            attrs={'class': 'form-select'},
            choices=empty_choice + [
                ('Alive', 'Alive'),
                ('Dead', 'Dead'),
                ('Unknown', 'Unknown')
            ]
        )

        # Date fields styling
        date_fields = [
            'birth_date', 'initial_diagnosis_date', 'transplant_date', 
            'admission_date', 'discharge_date', 'last_followup_date',
            'next_followup_date', 'donor_birth_date', 'acute_gvhd_date',
            'chronic_gvhd_date', 'neutrophil_engraftment_date',
            'platelets_engraftment_date', 'relapse_date', 'death_date',
            'conditioning_start_date'
        ]
        
        for field_name in date_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.DateInput(
                    attrs={
                        'type': 'date',
                        'class': 'form-control',
                        'placeholder': 'YYYY-MM-DD'
                    },
                    format='%Y-%m-%d'
                )

    def clean(self):
        cleaned_data = super().clean()
        
        # Auto-calculate disease category based on diagnosis
        diagnosis = cleaned_data.get('diagnosis')
        if diagnosis and diagnosis in DISEASE_CATEGORY_MAP:
            cleaned_data['disease_category'] = DISEASE_CATEGORY_MAP[diagnosis]
        
        return cleaned_data
 