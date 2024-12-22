from django.urls import path
from . import views
from .decorators import debug_login_required

app_name = 'event_reporting'

urlpatterns = [
    # Event Reporting URLs
    path('', debug_login_required(views.event_home), name='event_home'),
    path('event/new/', debug_login_required(views.event_form), name='event_new'),
    path('event/<int:event_number>/', debug_login_required(views.event_form), name='event_form'),
    path('event/list/', debug_login_required(views.event_list), name='event_list'),
    path('event/<int:event_number>/view/', debug_login_required(views.event_view), name='event_view'),
    path('event/<int:event_number>/comment/', debug_login_required(views.add_comment), name='add_comment'),
    path('event/<int:event_number>/assign/', debug_login_required(views.assign_event), name='assign_event'),
    path('qmo/dashboard/', debug_login_required(views.qmo_dashboard), name='qmo_dashboard'),
    path('qmo/export/', debug_login_required(views.export_reports), name='export_reports'),
    
    # Incident Reporting URLs (placeholders)
    path('incident/', debug_login_required(views.incident_home), name='incident_home'),
    path('event/<int:event_number>/qmo-scoring/', views.qmo_scoring, name='qmo_scoring'),
] 