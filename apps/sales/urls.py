from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST Framework router for ViewSets
router = DefaultRouter()
router.register(r'apartments', views.ApartmentInventoryViewSet, basename='apartment')
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'sales', views.SalesTransactionViewSet, basename='sales')
router.register(r'payments', views.CustomerPaymentScheduleViewSet, basename='payment')

urlpatterns = [
    # REST API endpoints
    path('', include(router.urls)),
]
