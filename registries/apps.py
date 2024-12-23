from django.apps import AppConfig
import os

class RegistriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'registries'
    verbose_name = 'Registries'
    path = os.path.dirname(os.path.abspath(__file__)) 