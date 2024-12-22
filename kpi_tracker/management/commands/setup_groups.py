from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from kpi_tracker.models import BreastKPI, ALLKPI, User

class Command(BaseCommand):
    help = 'Create default groups and permissions'

    def handle(self, *args, **options):
        # Create groups
        breast_team, _ = Group.objects.get_or_create(name='Breast Cancer Team')
        all_team, _ = Group.objects.get_or_create(name='ALL Team')
        analytics_team, _ = Group.objects.get_or_create(name='Analytics Team')
        admin_team, _ = Group.objects.get_or_create(name='Admin Team')

        # Get content types
        user_ct = ContentType.objects.get_for_model(User)

        # Create permissions
        view_breast_kpi = Permission.objects.get_or_create(
            codename='view_breast_kpi',
            name='Can view Breast Cancer KPIs',
            content_type=user_ct,
        )[0]
        edit_breast_kpi = Permission.objects.get_or_create(
            codename='edit_breast_kpi',
            name='Can edit Breast Cancer KPIs',
            content_type=user_ct,
        )[0]
        view_all_kpi = Permission.objects.get_or_create(
            codename='view_all_kpi',
            name='Can view ALL KPIs',
            content_type=user_ct,
        )[0]
        edit_all_kpi = Permission.objects.get_or_create(
            codename='edit_all_kpi',
            name='Can edit ALL KPIs',
            content_type=user_ct,
        )[0]
        view_analytics = Permission.objects.get_or_create(
            codename='view_analytics',
            name='Can view Analytics',
            content_type=user_ct,
        )[0]
        admin_access = Permission.objects.get_or_create(
            codename='admin_access',
            name='Has admin access',
            content_type=user_ct,
        )[0]

        # Assign permissions to Breast Cancer Team
        breast_team.permissions.add(view_breast_kpi, edit_breast_kpi, view_analytics)

        # Assign permissions to ALL Team
        all_team.permissions.add(view_all_kpi, edit_all_kpi, view_analytics)

        # Assign permissions to Analytics Team
        analytics_team.permissions.add(view_breast_kpi, view_all_kpi, view_analytics)

        # Assign permissions to Admin Team
        admin_team.permissions.add(
            view_breast_kpi, edit_breast_kpi,
            view_all_kpi, edit_all_kpi,
            view_analytics, admin_access
        )

        self.stdout.write(self.style.SUCCESS('Successfully set up groups and permissions')) 