"""
Customer Views
"""
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.sales.models import Customer
from apps.sales.serializers import CustomerSerializer, CustomerDetailSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for customer management"""
    queryset = Customer.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['customer_type']
    search_fields = ['first_name', 'last_name', 'id_number', 'email', 'phone']
    ordering_fields = ['last_name', 'first_name', 'created_at']
    ordering = ['last_name', 'first_name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        return CustomerSerializer
