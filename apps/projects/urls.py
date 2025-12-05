# in backend/apps/projects/urls.py

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    CityChoicesView,
    BankChoicesView,
    TransactionCategoryChoicesView,
    DashboardStatsView,
    FinancialKPIsView,
    ProjectFinancialKPIsView,
    MonthlyMonitoringView,
    ProjectViewSet,
    BankTransactionViewSet,
    ConstructionProgressViewSet,
    EquityDepositViewSet,
    ProjectDataInputsViewSet,
    ProjectDocumentViewSet
)

# Setup the router for the main Project model
router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

# Router for bank transactions
bank_router = DefaultRouter()
bank_router.register(r'', BankTransactionViewSet, basename='bank-transaction')

# Router for construction progress
construction_router = DefaultRouter()
construction_router.register(r'', ConstructionProgressViewSet, basename='construction-progress')

# Router for equity deposits
equity_router = DefaultRouter()
equity_router.register(r'', EquityDepositViewSet, basename='equity-deposit')

# Router for data inputs
data_inputs_router = DefaultRouter()
data_inputs_router.register(r'', ProjectDataInputsViewSet, basename='data-inputs')

# Router for documents
documents_router = DefaultRouter()
documents_router.register(r'', ProjectDocumentViewSet, basename='project-document')

urlpatterns = [
    # URLs for fetching choices for forms
    path('choices/cities/', CityChoicesView.as_view(), name='city-choices'),
    path('choices/banks/', BankChoicesView.as_view(), name='bank-choices'),
    path('choices/transaction-categories/', TransactionCategoryChoicesView.as_view(), name='transaction-category-choices'),

    # Dashboard stats
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),

    # Financial KPIs - Company-wide
    path('dashboard/financial-kpis/', FinancialKPIsView.as_view(), name='financial-kpis'),

    # Financial KPIs - Project-specific
    path('<int:project_pk>/financial-kpis/', ProjectFinancialKPIsView.as_view(), name='project-financial-kpis'),

    # Monthly Monitoring - Project-specific
    path('<int:project_pk>/monthly-monitoring/', MonthlyMonitoringView.as_view(), name='project-monthly-monitoring'),

    # Bank transactions URLs
    path('bank-transactions/', include(bank_router.urls)),

    # Construction progress URLs
    path('construction-progress/', include(construction_router.urls)),

    # Equity deposits URLs
    path('equity-deposits/', include(equity_router.urls)),

    # Data inputs URLs - for saving/loading project data sections
    re_path(
        r'^data-inputs/project/(?P<project_id>[^/.]+)/(?P<section_id>[^/.]+)/$',
        ProjectDataInputsViewSet.as_view({'get': 'handle_section', 'post': 'handle_section'}),
        name='project-data-inputs'
    ),

    # Project-specific equity deposits (nested under projects)
    path('<int:pk>/equity-deposits/', EquityDepositViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-equity-deposits'),
    path('<int:pk>/equity-deposits/<int:deposit_pk>/', EquityDepositViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='project-equity-deposit-detail'),

    # Documents URLs
    path('documents/', include(documents_router.urls)),

    # Include the main project URLs from the router
    path('', include(router.urls)),
]
