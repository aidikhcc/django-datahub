from django.urls import path
from . import views

app_name = 'registries'

urlpatterns = [
    path('bmt/', views.bmt_home, name='bmt_home'),
    path('bmt/form/', views.bmt_form, name='bmt_form'),
    path('bmt/form/<str:mrn>/<str:transplant_number>/', views.bmt_form, name='bmt_form_edit'),
    path('bmt/list/', views.bmt_list, name='bmt_list'),
    path('bmt/dashboard/', views.bmt_dashboard, name='bmt_dashboard'),
    path('bmt/followup/', views.bmt_followup, name='bmt_followup'),
    path('bmt/followup/complete/<str:mrn>/<str:transplant_number>/', 
         views.bmt_followup_complete, 
         name='bmt_followup_complete'),
] 