"""
Customer Payment Schedule Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.sales.models import CustomerPaymentSchedule
from apps.sales.serializers import (
    CustomerPaymentScheduleSerializer,
    CustomerPaymentScheduleCreateSerializer,
    PaymentMarkAsPaidSerializer,
)


class CustomerPaymentScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for customer payment schedule management"""
    queryset = CustomerPaymentSchedule.objects.select_related(
        'sales_transaction__customer',
        'sales_transaction__apartment'
    ).all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = {
        'sales_transaction': ['exact'],
        'payment_status': ['exact'],
        'payment_type': ['exact'],
        'scheduled_date': ['exact', 'gte', 'lte'],
    }
    search_fields = [
        'sales_transaction__customer__first_name',
        'sales_transaction__customer__last_name',
        'sales_transaction__apartment__unit_unique_id',
    ]
    ordering_fields = ['scheduled_date', 'payment_number', 'scheduled_amount']
    ordering = ['scheduled_date', 'payment_number']

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerPaymentScheduleCreateSerializer
        elif self.action == 'mark_paid':
            return PaymentMarkAsPaidSerializer
        return CustomerPaymentScheduleSerializer

    def create(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Payment create - received request.data: {request.data}")
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark payment as paid"""
        payment = self.get_object()
        serializer = PaymentMarkAsPaidSerializer(data=request.data)

        if serializer.is_valid():
            payment.mark_as_paid(
                amount=serializer.validated_data.get('actual_amount'),
                payment_date=serializer.validated_data.get('actual_date'),
                payment_method=serializer.validated_data.get('payment_method'),
            )

            # Update additional fields if provided
            if 'check_number' in serializer.validated_data:
                payment.check_number = serializer.validated_data['check_number']
            if 'bank_name' in serializer.validated_data:
                payment.bank_name = serializer.validated_data['bank_name']
            if 'reference_number' in serializer.validated_data:
                payment.reference_number = serializer.validated_data['reference_number']
            if 'notes' in serializer.validated_data:
                payment.notes = serializer.validated_data['notes']

            payment.save()

            return Response(CustomerPaymentScheduleSerializer(payment).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
