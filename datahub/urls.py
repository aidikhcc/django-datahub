from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('kpi/', include('kpi_tracker.urls')),
    path('events/', include('event_reporting.urls')),
    path('', lambda request: render(request, 'home.html'), name='home'),
] 