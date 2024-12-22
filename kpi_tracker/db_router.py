from .utils import get_db_password
from django.conf import settings

class AzureDBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'kpi_tracker':
            settings.DATABASES['default']['PASSWORD'] = get_db_password()
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'kpi_tracker':
            settings.DATABASES['default']['PASSWORD'] = get_db_password()
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True

    def get_password(self):
        return get_db_password() 