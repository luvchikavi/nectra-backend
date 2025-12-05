"""
Sales Transaction Serializers
"""
from rest_framework import serializers
from apps.sales.models import SalesTransaction, ApartmentInventory, Customer


class SalesTransactionSerializer(serializers.ModelSerializer):
    """Basic sales transaction serializer"""
    sale_status_display = serializers.CharField(source='get_sale_status_display', read_only=True)
    payment_terms_display = serializers.CharField(source='get_payment_terms_display', read_only=True)
    sale_type_display = serializers.CharField(source='get_sale_type_display', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    apartment_unit = serializers.CharField(source='apartment.unit_unique_id', read_only=True)
    total_paid = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()

    class Meta:
        model = SalesTransaction
        fields = [
            'id',
            'project',
            'apartment',
            'apartment_unit',
            'customer',
            'customer_name',
            'sale_type',
            'sale_type_display',
            'agreement_date',
            'contract_date',
            'delivery_date',
            'sale_status',
            'sale_status_display',
            'original_price',
            'discount_percent',
            'discount_amount',
            'final_price',
            'payment_terms',
            'payment_terms_display',
            'down_payment_amount',
            'mortgage_amount',
            'total_paid',
            'balance_due',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class SalesTransactionCreateSerializer(serializers.ModelSerializer):
    """Create sales transaction serializer"""

    class Meta:
        model = SalesTransaction
        fields = [
            'id',  # Include id in response
            'project',
            'apartment',
            'customer',
            'sale_type',
            'agreement_date',
            'contract_date',
            'delivery_date',
            'sale_status',
            'original_price',
            'discount_percent',
            'discount_amount',
            'final_price',
            'payment_terms',
            'down_payment_amount',
            'mortgage_amount',
            'notes',
        ]
        read_only_fields = ['id']  # id is auto-generated

    def validate_apartment(self, value):
        """Ensure apartment is available for sale"""
        if hasattr(value, 'sale_transaction'):
            raise serializers.ValidationError("This apartment is already sold")
        return value

    def create(self, validated_data):
        """Create sales transaction and update apartment status"""
        # Set created_by from request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user

        return super().create(validated_data)


class SalesTransactionDetailSerializer(serializers.ModelSerializer):
    """Detailed sales transaction serializer with related data"""
    sale_status_display = serializers.CharField(source='get_sale_status_display', read_only=True)
    payment_terms_display = serializers.CharField(source='get_payment_terms_display', read_only=True)
    sale_type_display = serializers.CharField(source='get_sale_type_display', read_only=True)
    customer_details = serializers.SerializerMethodField()
    apartment_details = serializers.SerializerMethodField()
    payment_schedule = serializers.SerializerMethodField()
    total_paid = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()

    class Meta:
        model = SalesTransaction
        fields = [
            'id',
            'project',
            'apartment',
            'apartment_details',
            'customer',
            'customer_details',
            'sale_type',
            'sale_type_display',
            'agreement_date',
            'contract_date',
            'delivery_date',
            'sale_status',
            'sale_status_display',
            'original_price',
            'discount_percent',
            'discount_amount',
            'final_price',
            'payment_terms',
            'payment_terms_display',
            'down_payment_amount',
            'mortgage_amount',
            'total_paid',
            'balance_due',
            'payment_schedule',
            'notes',
            'contract_file',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def get_customer_details(self, obj):
        """Get customer details"""
        from .customer_serializers import CustomerSerializer
        return CustomerSerializer(obj.customer).data

    def get_apartment_details(self, obj):
        """Get apartment details"""
        from .apartment_serializers import ApartmentInventorySerializer
        return ApartmentInventorySerializer(obj.apartment).data

    def get_payment_schedule(self, obj):
        """Get payment schedule"""
        from .payment_serializers import CustomerPaymentScheduleSerializer
        payments = obj.payment_schedule.all()
        return CustomerPaymentScheduleSerializer(payments, many=True).data
