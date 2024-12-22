from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Synchronize auth tables'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Insert content types
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM [datahub].[django_content_type] WHERE [app_label] = 'auth' AND [model] = 'permission')
                INSERT INTO [datahub].[django_content_type] ([app_label], [model]) VALUES ('auth', 'permission');
                
                IF NOT EXISTS (SELECT 1 FROM [datahub].[django_content_type] WHERE [app_label] = 'auth' AND [model] = 'group')
                INSERT INTO [datahub].[django_content_type] ([app_label], [model]) VALUES ('auth', 'group');
                
                IF NOT EXISTS (SELECT 1 FROM [datahub].[django_content_type] WHERE [app_label] = 'kpi_tracker' AND [model] = 'user')
                INSERT INTO [datahub].[django_content_type] ([app_label], [model]) VALUES ('kpi_tracker', 'user');
            """)

            # Insert basic permissions
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM [datahub].[auth_permission] WHERE [codename] = 'add_user')
                INSERT INTO [datahub].[auth_permission] ([name], [content_type_id], [codename])
                SELECT 'Can add user', ct.id, 'add_user'
                FROM [datahub].[django_content_type] ct
                WHERE ct.app_label = 'kpi_tracker' AND ct.model = 'user';
            """)

            self.stdout.write(self.style.SUCCESS('Successfully synchronized auth tables'))