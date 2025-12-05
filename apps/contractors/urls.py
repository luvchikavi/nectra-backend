"""
Contractor Module URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ContractorViewSet,
    ContractorProfileViewSet,
    InvoiceViewSet,
    InvoiceApprovalViewSet,
    ActualCostViewSet
)

router = DefaultRouter()
router.register(r'contractors', ContractorViewSet, basename='contractor')
router.register(r'profile', ContractorProfileViewSet, basename='contractor-profile')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'approvals', InvoiceApprovalViewSet, basename='invoice-approval')
router.register(r'actual-costs', ActualCostViewSet, basename='actual-cost')

urlpatterns = [
    path('', include(router.urls)),
]
