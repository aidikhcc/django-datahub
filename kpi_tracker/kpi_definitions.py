BREAST_KPI_DEFINITIONS = {
    'treatment_start': {
        'title': 'Time to Start Treatment',
        'definition': 'Number of active malignant disease patients who started treatment within one month from insurance approval',
        'target': '80%',
        'rationale': 'To ensure timely initiation of treatment for better outcomes',
        'excluded': 'Non-malignant cases, palliative cases',
        'calculation': lambda entry: {
            'within_target': (entry.Treatment_date - entry.Insurance_date).days <= 31 
            if entry.Treatment_date and entry.Insurance_date and not entry.Treatment_NotFitForThisKPI else None,
            'days': (entry.Treatment_date - entry.Insurance_date).days + 1 
            if entry.Treatment_date and entry.Insurance_date else None
        }
    },
    'surgery': {
        'title': 'Surgery After Neoadjuvant Chemotherapy',
        'definition': 'Time between last dose of neoadjuvant chemotherapy and breast surgery is a maximum of 8 weeks',
        'target': '80%',
        'rationale': 'To decrease the risk of disease progression',
        'excluded': 'Palliative mastectomy',
        'calculation': lambda entry: {
            'within_target': (entry.Surgery_date - entry.Neoadjuvant_ctx_date).days <= 56 
            if entry.Surgery_date and entry.Neoadjuvant_ctx_date else None,
            'days': (entry.Surgery_date - entry.Neoadjuvant_ctx_date).days + 1 
            if entry.Surgery_date and entry.Neoadjuvant_ctx_date else None
        }
    },
    'radiotherapy': {
        'title': 'Radiotherapy After Surgery/Chemotherapy',
        'definition': 'Time between surgery (or last dose of adjuvant chemotherapy if given) and adjuvant radiotherapy is a maximum of 8 weeks',
        'target': '80%',
        'rationale': 'To decrease the risk of local disease recurrence',
        'excluded': 'Palliative patients',
        'calculation': lambda entry: {
            'within_target': (entry.Radio_date - entry.surgery_last_dose_adjuvant_chemotherapy_date).days <= 56 
            if entry.Radio_date and entry.surgery_last_dose_adjuvant_chemotherapy_date else None,
            'days': (entry.Radio_date - entry.surgery_last_dose_adjuvant_chemotherapy_date).days + 1 
            if entry.Radio_date and entry.surgery_last_dose_adjuvant_chemotherapy_date else None
        }
    },
    'biopsy': {
        'title': 'Breast Biopsy Turn Around Time',
        'definition': 'All breast biopsies reported within 4 working days from acceptance date',
        'target': '80%',
        'rationale': 'Timely results of pathology findings are required to manage patients within specified time frame',
        'excluded': 'Specimens delayed for financial issues, technical failures, holidays and weekends, excisional specimens'
    }
} 