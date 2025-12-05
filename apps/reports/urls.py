"""
Reports App URLs
"""

from django.urls import path
from .views import AvailableModulesView, GenerateReportView

urlpatterns = [
    path('modules/', AvailableModulesView.as_view(), name='report-modules'),
    path('generate/', GenerateReportView.as_view(), name='generate-report'),
]
