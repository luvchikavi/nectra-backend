"""
Customer Payment Schedule Serializers
"""
from rest_framework import serializers
from apps.sales.models import CustomerPaymentSchedule, SalesTransaction


class CustomerPaymentScheduleSerializer(serializers.ModelSerializer):
    """Customer payment schedule serializer"""
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()
    customer_name = serializers.CharField(source='sales_transaction.customer.full_name', read_only=True)

    class Meta:
        model = CustomerPaymentSchedule
        fields = [
            'id',
            'sales_transaction',
            'customer_name',
            'payment_number',
            'payment_type',
            'payment_type_display',
            'payment_description',
            'scheduled_amount',
            'scheduled_date',
            'actual_amount',
            'actual_date',
            'payment_status',
            'payment_status_display',
            'payment_method',
            'payment_method_display',
            'check_number',
            'bank_name',
            'reference_number',
            'days_delay',
            'is_overdue',
            'balance_due',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'days_delay', 'created_at', 'updated_at']


class CustomerPaymentScheduleCreateSerializer(serializers.ModelSerializer):
    """Create payment schedule serializer"""

    class Meta:
        model = CustomerPaymentSchedule
        fields = [
            'sales_transaction',
            'payment_number',
            'payment_type',
            'payment_description',
            'scheduled_amount',
            'scheduled_date',
            'payment_status',
            'notes',
        ]

    def validate(self, data):
        """Validate payment schedule data"""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Payment validation - received data: {data}")

        # Ensure payment number is unique for this sales transaction
        sales_transaction = data.get('sales_transaction')
        payment_number = data.get('payment_number')

        if sales_transaction and payment_number:
            existing = CustomerPaymentSchedule.objects.filter(
                sales_transaction=sales_transaction,
                payment_number=payment_number
            ).exists()

            if existing:
                raise serializers.ValidationError(
                    f"Payment #{payment_number} already exists for this transaction"
                )

        return data


class PaymentMarkAsPaidSerializer(serializers.Serializer):
    """Serializer for marking payment as paid"""
    actual_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        help_text="Amount actually paid (defaults to scheduled amount)"
    )
    actual_date = serializers.DateField(
        required=False,
        help_text="Date of payment (defaults to today)"
    )
    payment_method = serializers.ChoiceField(
        choices=CustomerPaymentSchedule.PAYMENT_METHODS,
        required=False,
        help_text="Payment method used"
    )
    check_number = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Check number if applicable"
    )
    bank_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Bank name"
    )
    reference_number = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Reference/transaction number"
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Additional notes"
    )


class BulkPaymentScheduleCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating payment schedules"""
    sales_transaction = serializers.PrimaryKeyRelatedField(
        queryset=SalesTransaction.objects.all()
    )
    payments = CustomerPaymentScheduleCreateSerializer(many=True)

    def create(self, validated_data):
        """Create multiple payment schedules"""
        from apps.sales.models import SalesTransaction

        sales_transaction = validated_data['sales_transaction']
        payments_data = validated_data['payments']

        payments = []
        for payment_data in payments_data:
            payment_data['sales_transaction'] = sales_transaction
            payment = CustomerPaymentSchedule(**payment_data)
            payments.append(payment)

        return CustomerPaymentSchedule.objects.bulk_create(payments)
