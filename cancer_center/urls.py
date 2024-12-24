from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
    path('', include('kpi_tracker.urls')),
    path('events/', include('event_reporting.urls')),
    path('registries/', include('registries.urls')),
] 