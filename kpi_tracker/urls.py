from django.urls import path, re_path
from django.shortcuts import redirect
from . import views

app_name = 'kpi_tracker'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('oauth2/callback/', views.auth_callback, name='auth_callback'),
    
    # KPI Disease Management home
    path('', views.kpi_home, name='kpi_home'),
    
    # Default redirect for breast
    path('breast/', lambda request: redirect('kpi_tracker:breast_form'), name='breast'),
    
    # Breast KPI URLs
    path('breast/form/', views.breast_kpi_form, name='breast_form'),
    path('breast/form/<str:mrn>/', views.breast_kpi_form, name='breast_form_edit'),
    path('breast/list/', views.breast_kpi_list, name='breast_list'),
    path('breast/analytics/', views.breast_kpi_analytics, name='breast_analytics'),
    path('breast/followup/', views.breast_kpi_followup, name='breast_followup'),
    path('breast/dashboard/', views.breast_kpi_dashboard, name='breast_kpi_dashboard'),
    re_path(r'^breast/dashboard/filter/?$', views.breast_kpi_dashboard_filter, name='breast_dashboard_filter'),
] 





