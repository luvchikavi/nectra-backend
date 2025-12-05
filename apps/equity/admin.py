from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Q
from .models import (
    EquityRequirement,
    EquityTransaction,
    EquitySnapshot,
    EquityApprovalHistory
)


@admin.register(EquityRequirement)
class EquityRequirementAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'bank_name',
        'required_percentage',
        'required_amount_display',
        'deadline_date',
        'created_at'
    ]
    list_filter = ['bank_name', 'created_at']
    search_fields = ['project__project_name', 'bank_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Project Information', {
            'fields': ('project', 'bank_name')
        }),
        ('Equity Requirements', {
            'fields': ('required_percentage', 'required_amount_nis', 'deadline_date')
        }),
        ('Additional Information', {
            'fields': ('notes', 'updated_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def required_amount_display(self, obj):
        return format_html(
            '<strong>{:,.2f} ₪</strong>',
            obj.required_amount_nis
        )
    required_amount_display.short_description = 'Required Amount'


class EquityApprovalHistoryInline(admin.TabularInline):
    model = EquityApprovalHistory
    extra = 0
    readonly_fields = ['action', 'previous_status', 'new_status',
                      'previous_amount', 'new_amount', 'action_by',
                      'action_date', 'notes']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(EquityTransaction)
class EquityTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_date',
        'project',
        'transaction_type',
        'paid_amount_display',
        'approved_amount_display',
        'approval_status_display',
        'submitted_by',
        'validated_by',
        'validated_date'
    ]
    list_filter = [
        'approval_status',
        'transaction_type',
        'transaction_date',
        'validated_date'
    ]
    search_fields = [
        'project__project_name',
        'supplier_name',
        'invoice_number',
        'receipt_number'
    ]
    readonly_fields = ['created_at', 'updated_at', 'get_equity_value']
    
    fieldsets = (
        ('Project & Transaction Info', {
            'fields': (
                'project',
                'transaction_type',
                'transaction_date'
            )
        }),
        ('Financial Details', {
            'fields': (
                'paid_amount_nis',
                'approved_amount_nis',
                'get_equity_value'
            )
        }),
        ('Source Tracking', {
            'fields': (
                'source_calculator',
                'source_line_id'
            ),
            'classes': ('collapse',)
        }),
        ('Documentation', {
            'fields': (
                'payment_proof',
                'invoice_number',
                'receipt_number',
                'check_number',
                'bank_transfer_ref',
                'supplier_name'
            ),
            'classes': ('collapse',)
        }),
        ('Validation Workflow', {
            'fields': (
                'approval_status',
                'submitted_for_validation_date',
                'submitted_by',
                'validated_date',
                'validated_by',
                'rejection_reason'
            )
        }),
        ('Notes', {
            'fields': ('appraiser_notes', 'manager_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EquityApprovalHistoryInline]
    
    def paid_amount_display(self, obj):
        return format_html(
            '<strong>{:,.2f} ₪</strong>',
            obj.paid_amount_nis
        )
    paid_amount_display.short_description = 'Paid Amount'
    
    def approved_amount_display(self, obj):
        if obj.approved_amount_nis:
            color = 'green' if obj.approved_amount_nis == obj.paid_amount_nis else 'orange'
            return format_html(
                '<span style="color: {};">{:,.2f} ₪</span>',
                color,
                obj.approved_amount_nis
            )
        return '-'
    approved_amount_display.short_description = 'Validated Amount'
    
    def approval_status_display(self, obj):
        colors = {
            'DRAFT': '#9E9E9E',
            'PENDING_VALIDATION': '#FFA500',
            'VALIDATED': '#4CAF50',
            'REJECTED': '#F44336',
            'APPROVED_BANK': '#2196F3'
        }
        color = colors.get(obj.approval_status, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_approval_status_display()
        )
    approval_status_display.short_description = 'Status'
    
    def get_equity_value(self, obj):
        value = obj.get_equity_value()
        if value > 0:
            return format_html(
                '<strong style="color: green;">{:,.2f} ₪</strong>',
                value
            )
        return format_html('<span style="color: gray;">0.00 ₪</span>')
    get_equity_value.short_description = 'Equity Value'
    
    def save_model(self, request, obj, form, change):
        # Auto-create approval history
        if change:
            old_obj = EquityTransaction.objects.get(pk=obj.pk)
            
            # Status changed
            if old_obj.approval_status != obj.approval_status:
                EquityApprovalHistory.objects.create(
                    transaction=obj,
                    action='STATUS_CHANGED',
                    previous_status=old_obj.approval_status,
                    new_status=obj.approval_status,
                    action_by=request.user,
                    notes=f"Status changed from {old_obj.get_approval_status_display()} to {obj.get_approval_status_display()}"
                )
            
            # Amount changed
            if old_obj.approved_amount_nis != obj.approved_amount_nis:
                EquityApprovalHistory.objects.create(
                    transaction=obj,
                    action='AMOUNT_CHANGED',
                    previous_amount=old_obj.approved_amount_nis,
                    new_amount=obj.approved_amount_nis,
                    action_by=request.user,
                    notes=f"Validated amount changed"
                )
        else:
            # New transaction - default to DRAFT
            if not obj.submitted_by:
                obj.submitted_by = request.user
        
        super().save_model(request, obj, form, change)


@admin.register(EquitySnapshot)
class EquitySnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'snapshot_date',
        'project',
        'required_equity_display',
        'validated_equity_display',
        'equity_gap_display',
        'is_sufficient',
        'generated_for_bank',
        'bank_name'
    ]
    list_filter = [
        'generated_for_bank',
        'snapshot_date',
        'bank_name'
    ]
    search_fields = ['project__project_name', 'bank_name']
    readonly_fields = ['created_at', 'is_equity_sufficient', 'calculate_gap_percentage']
    
    fieldsets = (
        ('Snapshot Information', {
            'fields': (
                'project',
                'snapshot_date'
            )
        }),
        ('Project Costs', {
            'fields': (
                'total_project_cost',
                'required_equity_percentage',
                'required_equity_amount'
            )
        }),
        ('Equity Status', {
            'fields': (
                'validated_equity_total',
                'pending_validation_total',
                'equity_gap',
                'equity_gap_percentage',
                'is_equity_sufficient'
            )
        }),
        ('Bank Submission', {
            'fields': (
                'generated_for_bank',
                'bank_name',
                'bank_submission_date'
            )
        }),
        ('Snapshot Data', {
            'fields': ('transactions_snapshot',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def required_equity_display(self, obj):
        return format_html(
            '<strong>{:,.2f} ₪</strong><br><small>({:.1f}%)</small>',
            obj.required_equity_amount,
            obj.required_equity_percentage
        )
    required_equity_display.short_description = 'Required Equity'
    
    def validated_equity_display(self, obj):
        return format_html(
            '<strong style="color: green;">{:,.2f} ₪</strong>',
            obj.validated_equity_total
        )
    validated_equity_display.short_description = 'Validated Equity'
    
    def equity_gap_display(self, obj):
        if obj.equity_gap <= 0:
            return format_html(
                '<strong style="color: green;">✓ Surplus: {:,.2f} ₪</strong>',
                abs(obj.equity_gap)
            )
        else:
            return format_html(
                '<strong style="color: red;">⚠ Gap: {:,.2f} ₪</strong>',
                obj.equity_gap
            )
    equity_gap_display.short_description = 'Equity Gap'
    
    def is_sufficient(self, obj):
        if obj.is_equity_sufficient():
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    is_sufficient.short_description = 'Sufficient?'


@admin.register(EquityApprovalHistory)
class EquityApprovalHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'action_date',
        'transaction',
        'action',
        'action_by',
        'status_change',
        'amount_change'
    ]
    list_filter = ['action', 'action_date']
    search_fields = ['transaction__project__project_name', 'notes']
    readonly_fields = [
        'transaction',
        'action',
        'previous_status',
        'new_status',
        'previous_amount',
        'new_amount',
        'action_by',
        'action_date'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def status_change(self, obj):
        if obj.previous_status and obj.new_status:
            return format_html(
                '{} → {}',
                obj.previous_status,
                obj.new_status
            )
        return '-'
    status_change.short_description = 'Status Change'
    
    def amount_change(self, obj):
        if obj.previous_amount is not None and obj.new_amount is not None:
            return format_html(
                '{:,.2f} → {:,.2f} ₪',
                obj.previous_amount,
                obj.new_amount
            )
        return '-'
    amount_change.short_description = 'Amount Change'
