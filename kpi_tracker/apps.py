from django.apps import AppConfig

class KpiTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kpi_tracker'
    
    def ready(self):
        # Import signals or perform other initialization
        pass 