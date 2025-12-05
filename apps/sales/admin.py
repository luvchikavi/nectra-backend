from django.contrib import admin
from .models import (
    Customer,
    ApartmentInventory,
    SalesTransaction,
    SalesLine,
    CustomerPaymentSchedule,
    UnitMix,
    SalesForecast
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'id_number', 'phone', 'email', 'customer_type'
    ]
    list_filter = ['customer_type']
    search_fields = ['first_name', 'last_name', 'id_number', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ApartmentInventory)
class ApartmentInventoryAdmin(admin.ModelAdmin):
    list_display = [
        'unit_unique_id', 'project', 'building_number', 'floor',
        'unit_number', 'unit_type', 'room_count', 'unit_status',
        'list_price_with_vat', 'get_customer_name'
    ]
    list_filter = ['project', 'unit_type', 'unit_status', 'building_number', 'floor']
    search_fields = ['unit_unique_id', 'customer_first_name', 'customer_last_name']
    readonly_fields = ['created_at', 'updated_at', 'unit_unique_id']

    def get_customer_name(self, obj):
        return obj.customer_full_name
    get_customer_name.short_description = 'Customer'

    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'building_number', 'wing', 'floor', 'unit_number',
                      'plan_number', 'unit_unique_id')
        }),
        ('Unit Details', {
            'fields': ('unit_type', 'unit_sub_type', 'room_count', 'unit_direction')
        }),
        ('Areas', {
            'fields': ('net_area_sqm', 'gross_area_sqm', 'unit_area_sqm',
                      'balcony_area_sqm', 'terrace_area_sqm', 'roof_terrace_area_sqm',
                      'yard_area_sqm', 'gallery_area_sqm')
        }),
        ('Parking & Storage', {
            'fields': ('parking_spaces', 'storage_count')
        }),
        ('Pricing', {
            'fields': ('price_per_sqm_equivalent_with_vat', 'price_per_sqm_net_with_vat',
                      'list_price_with_vat', 'list_price_no_vat',
                      'discount_percent', 'discount_amount',
                      'final_price_with_vat', 'final_price_no_vat', 'vat_rate')
        }),
        ('Sale Information', {
            'fields': ('unit_status', 'contract_date', 'expected_delivery_date')
        }),
        ('Customer Information', {
            'fields': ('customer', 'customer_first_name', 'customer_last_name', 'sell_contract')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SalesTransaction)
class SalesTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'project', 'get_apartment', 'get_customer',
        'contract_date', 'final_price', 'sale_status'
    ]
    list_filter = ['project', 'sale_status', 'sale_type', 'payment_terms', 'contract_date']
    search_fields = ['customer__first_name', 'customer__last_name',
                    'apartment__unit_unique_id']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    date_hierarchy = 'contract_date'

    def get_apartment(self, obj):
        return obj.apartment.unit_unique_id if obj.apartment else '-'
    get_apartment.short_description = 'Apartment'

    def get_customer(self, obj):
        return obj.customer.full_name if obj.customer else '-'
    get_customer.short_description = 'Customer'


@admin.register(CustomerPaymentSchedule)
class CustomerPaymentScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'get_sales_transaction', 'get_customer_name', 'payment_number',
        'payment_type', 'scheduled_amount', 'scheduled_date',
        'payment_status', 'days_delay'
    ]
    list_filter = ['payment_status', 'payment_type', 'payment_method', 'scheduled_date']
    search_fields = ['sales_transaction__customer__first_name',
                    'sales_transaction__customer__last_name',
                    'sales_transaction__apartment__unit_unique_id']
    readonly_fields = ['created_at', 'updated_at', 'days_delay']
    date_hierarchy = 'scheduled_date'

    def get_sales_transaction(self, obj):
        return str(obj.sales_transaction)
    get_sales_transaction.short_description = 'Sales Transaction'

    def get_customer_name(self, obj):
        return obj.sales_transaction.customer.full_name
    get_customer_name.short_description = 'Customer'

    fieldsets = (
        ('Links', {
            'fields': ('sales_transaction',)
        }),
        ('Payment Plan', {
            'fields': ('payment_number', 'payment_type', 'payment_description')
        }),
        ('Scheduled Payment', {
            'fields': ('scheduled_amount', 'scheduled_date')
        }),
        ('Actual Payment', {
            'fields': ('actual_amount', 'actual_date', 'payment_status')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'check_number', 'bank_name',
                      'reference_number', 'days_delay', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UnitMix)
class UnitMixAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'apartment_type', 'units_count',
        'avg_net_area', 'avg_gross_area', 'is_penthouse', 'is_duplex'
    ]
    list_filter = ['project', 'is_penthouse', 'is_duplex']
    search_fields = ['apartment_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SalesForecast)
class SalesForecastAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'month_year', 'forecast_date',
        'expected_sales_count', 'expected_revenue_nis',
        'cumulative_sales_count', 'cumulative_revenue_nis'
    ]
    list_filter = ['project', 'forecast_date']
    search_fields = ['month_year']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    date_hierarchy = 'forecast_date'
