"""
Apartment Inventory Serializers
"""
from rest_framework import serializers
from apps.sales.models import ApartmentInventory, Customer


class ApartmentInventoryListSerializer(serializers.ModelSerializer):
    """List serializer for apartment inventory (grid view)"""
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    unit_status_display = serializers.CharField(source='get_unit_status_display', read_only=True)
    customer_name = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = ApartmentInventory
        fields = [
            'id',
            'project',
            'project_name',
            'unit_unique_id',
            'building_number',
            'wing',
            'floor',
            'unit_number',
            'plan_number',
            'unit_type',
            'unit_type_display',
            'unit_sub_type',
            'room_count',
            'unit_direction',
            'net_area_sqm',
            'gross_area_sqm',
            'unit_area_sqm',
            'balcony_area_sqm',
            'terrace_area_sqm',
            'roof_terrace_area_sqm',
            'yard_area_sqm',
            'parking_spaces',
            'storage_count',
            'price_per_sqm_net_with_vat',
            'list_price_with_vat',
            'discount_percent',
            'discount_amount',
            'final_price',
            'unit_status',
            'unit_status_display',
            'customer_name',
            'contract_date',
        ]

    def get_customer_name(self, obj):
        """Get customer full name"""
        return obj.customer_full_name

    def get_final_price(self, obj):
        """Get final price"""
        price = obj.calculate_final_price_with_vat()
        return float(price) if price else None


class ApartmentInventorySerializer(serializers.ModelSerializer):
    """Full apartment inventory serializer"""
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    unit_status_display = serializers.CharField(source='get_unit_status_display', read_only=True)
    customer_name = serializers.SerializerMethodField()
    is_sold = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = ApartmentInventory
        fields = [
            'id',
            'project',
            'unit_unique_id',
            'building_number',
            'wing',
            'floor',
            'unit_number',
            'plan_number',
            'unit_type',
            'unit_type_display',
            'unit_sub_type',
            'room_count',
            'unit_direction',
            # Areas
            'net_area_sqm',
            'gross_area_sqm',
            'unit_area_sqm',
            'balcony_area_sqm',
            'terrace_area_sqm',
            'roof_terrace_area_sqm',
            'yard_area_sqm',
            'gallery_area_sqm',
            # Parking and Storage
            'parking_spaces',
            'storage_count',
            # Pricing
            'price_per_sqm_equivalent_with_vat',
            'price_per_sqm_net_with_vat',
            'price_per_sqm_no_vat',
            'list_price_with_vat',
            'list_price_no_vat',
            'discount_percent',
            'discount_amount',
            'final_price_with_vat',
            'final_price_no_vat',
            'vat_rate',
            # Status
            'unit_status',
            'unit_status_display',
            'contract_date',
            'expected_delivery_date',
            # Customer
            'customer',
            'customer_name',
            'customer_first_name',
            'customer_last_name',
            # Flags
            'is_sold',
            'is_available',
            # Metadata
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'unit_unique_id', 'created_at', 'updated_at']

    def get_customer_name(self, obj):
        """Get customer full name"""
        return obj.customer_full_name


class ApartmentInventoryDetailSerializer(serializers.ModelSerializer):
    """Detailed apartment serializer with related data"""
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    unit_status_display = serializers.CharField(source='get_unit_status_display', read_only=True)
    customer_details = serializers.SerializerMethodField()
    sale_transaction = serializers.SerializerMethodField()
    total_area = serializers.SerializerMethodField()

    class Meta:
        model = ApartmentInventory
        fields = [
            'id',
            'project',
            'unit_unique_id',
            'building_number',
            'wing',
            'floor',
            'unit_number',
            'plan_number',
            'unit_type',
            'unit_type_display',
            'unit_sub_type',
            'room_count',
            'unit_direction',
            # Areas
            'net_area_sqm',
            'gross_area_sqm',
            'unit_area_sqm',
            'balcony_area_sqm',
            'terrace_area_sqm',
            'roof_terrace_area_sqm',
            'yard_area_sqm',
            'gallery_area_sqm',
            'total_area',
            # Parking and Storage
            'parking_spaces',
            'storage_count',
            # Pricing
            'price_per_sqm_equivalent_with_vat',
            'price_per_sqm_net_with_vat',
            'price_per_sqm_no_vat',
            'list_price_with_vat',
            'list_price_no_vat',
            'discount_percent',
            'discount_amount',
            'final_price_with_vat',
            'final_price_no_vat',
            'vat_rate',
            # Status
            'unit_status',
            'unit_status_display',
            'contract_date',
            'expected_delivery_date',
            # Customer
            'customer',
            'customer_details',
            'customer_first_name',
            'customer_last_name',
            # Sale Transaction
            'sale_transaction',
            # Metadata
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'unit_unique_id', 'created_at', 'updated_at']

    def get_customer_details(self, obj):
        """Get customer details if exists"""
        if obj.customer:
            from .customer_serializers import CustomerSerializer
            return CustomerSerializer(obj.customer).data
        return None

    def get_sale_transaction(self, obj):
        """Get sale transaction if exists"""
        if hasattr(obj, 'sale_transaction'):
            from .sales_serializers import SalesTransactionSerializer
            return SalesTransactionSerializer(obj.sale_transaction).data
        return None

    def get_total_area(self, obj):
        """Get total area"""
        return float(obj.total_area())


class ApartmentBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk apartment creation"""
    apartments = ApartmentInventorySerializer(many=True)

    def create(self, validated_data):
        apartments_data = validated_data.get('apartments', [])
        apartments = [
            ApartmentInventory(**apartment_data)
            for apartment_data in apartments_data
        ]
        return ApartmentInventory.objects.bulk_create(apartments)
