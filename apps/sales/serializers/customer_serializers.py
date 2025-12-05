"""
Customer Serializers
"""
from rest_framework import serializers
from apps.sales.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Basic customer serializer"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'id_number',
            'phone',
            'email',
            'customer_type',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Detailed customer serializer with related data"""
    full_name = serializers.ReadOnlyField()
    purchases_count = serializers.SerializerMethodField()
    total_purchased = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'id_number',
            'phone',
            'email',
            'address',
            'customer_type',
            'notes',
            'purchases_count',
            'total_purchased',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_purchases_count(self, obj):
        """Get number of purchases"""
        return obj.purchases.count()

    def get_total_purchased(self, obj):
        """Get total amount purchased"""
        total = sum(purchase.final_price for purchase in obj.purchases.all())
        return float(total)
