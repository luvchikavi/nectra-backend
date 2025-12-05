# in backend/apps/budget/urls.py

from django.urls import path
from .views import MonthlyBudgetReportViewSet

urlpatterns = [
    # Manual URL patterns for clearer API structure
    path(
        'projects/<int:project_pk>/reports/',
        MonthlyBudgetReportViewSet.as_view({
            'get': 'list',
        }),
        name='project-budget-reports-list'
    ),
    path(
        'projects/<int:project_pk>/reports/generate-report/',
        MonthlyBudgetReportViewSet.as_view({
            'post': 'generate_report',
        }),
        name='project-budget-reports-generate'
    ),
    path(
        'projects/<int:project_pk>/reports/latest/',
        MonthlyBudgetReportViewSet.as_view({
            'get': 'retrieve',
        }),
        name='project-budget-reports-latest'
    ),
    path(
        'projects/<int:project_pk>/reports/<int:pk>/',
        MonthlyBudgetReportViewSet.as_view({
            'get': 'retrieve',
        }),
        name='project-budget-reports-detail'
    ),
    path(
        'projects/<int:project_pk>/reports/<int:year>/<int:month>/',
        MonthlyBudgetReportViewSet.as_view({
            'get': 'retrieve',
        }),
        name='project-budget-reports-by-date'
    ),
]
