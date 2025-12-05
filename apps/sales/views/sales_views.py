"""
Sales Transaction Views
"""
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.sales.models import SalesTransaction
from apps.sales.serializers import (
    SalesTransactionSerializer,
    SalesTransactionCreateSerializer,
    SalesTransactionDetailSerializer,
)


class SalesTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for sales transaction management"""
    queryset = SalesTransaction.objects.select_related(
        'project', 'apartment', 'customer'
    ).all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = {
        'project': ['exact'],
        'sale_status': ['exact'],
        'sale_type': ['exact'],
        'payment_terms': ['exact'],
        'contract_date': ['exact', 'gte', 'lte'],
    }
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'apartment__unit_unique_id',
    ]
    ordering_fields = ['contract_date', 'final_price', 'created_at']
    ordering = ['-contract_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return SalesTransactionCreateSerializer
        elif self.action == 'retrieve':
            return SalesTransactionDetailSerializer
        return SalesTransactionSerializer
