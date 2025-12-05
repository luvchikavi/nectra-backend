from django.contrib import admin
from .models import Contractor, Invoice, InvoiceApproval, ActualCost


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'tax_id', 'contact_name', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['company_name', 'tax_id', 'contact_name', 'email']
    filter_horizontal = ['projects']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'contractor', 'project', 'vendor_name', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'category', 'project', 'created_at']
    search_fields = ['invoice_number', 'vendor_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'ocr_raw_data', 'ocr_confidence']
    raw_id_fields = ['contractor', 'project', 'construction_progress', 'bank_transaction', 'uploaded_by']


@admin.register(InvoiceApproval)
class InvoiceApprovalAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'action', 'approved_by', 'created_at']
    list_filter = ['action', 'created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['invoice', 'approved_by']


@admin.register(ActualCost)
class ActualCostAdmin(admin.ModelAdmin):
    list_display = ['project', 'year', 'month', 'category', 'total_gross', 'invoice_count', 'last_updated']
    list_filter = ['project', 'year', 'month', 'category']
    readonly_fields = ['last_updated']
