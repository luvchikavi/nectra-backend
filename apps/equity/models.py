from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class EquityRequirement(models.Model):
    """Bank's equity requirement for a project"""
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='equity_requirements'
    )
    bank_name = models.CharField(max_length=200, verbose_name="Bank Name")
    required_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Required Equity %",
        help_text="e.g., 25.00 for 25%"
    )
    required_amount_nis = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Required Amount (NIS)",
        help_text="Calculated: Total Project Cost × Required %"
    )
    deadline_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Equity Deadline"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='equity_requirements_updated'
    )
    
    class Meta:
        verbose_name = "Equity Requirement"
        verbose_name_plural = "Equity Requirements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project} - {self.bank_name} ({self.required_percentage}%)"
    
    def calculate_required_amount(self, total_project_cost):
        """Calculate required equity based on project cost"""
        return total_project_cost * (self.required_percentage / Decimal('100'))


class EquityTransaction(models.Model):
    """Any transaction that might count toward equity"""
    
    TRANSACTION_TYPES = [
        ('CASH_DEPOSIT', 'Cash Deposit'),
        ('LAND_PURCHASE', 'Land Purchase'),
        ('CONSULTANT_FEE', 'Consultant Fee'),
        ('DEV_LEVY', 'Development Levy'),
        ('PURCHASE_TAX', 'Purchase Tax'),
        ('PLANNING_FEE', 'Planning Fee'),
        ('ARCHITECT_FEE', 'Architect Fee'),
        ('ENGINEER_FEE', 'Engineer Fee'),
        ('LAWYER_FEE', 'Lawyer Fee'),
        ('SURVEY_FEE', 'Survey Fee'),
        ('OTHER_EXPENSE', 'Other Expense'),
    ]
    
    APPROVAL_STATUS = [
        ('DRAFT', 'Draft (Not Submitted)'),
        ('PENDING_VALIDATION', 'Pending Team Manager Validation'),
        ('VALIDATED', 'Validated by Team Manager'),
        ('REJECTED', 'Rejected by Team Manager'),
        ('APPROVED_BANK', 'Approved by Bank'),
    ]
    
    # Basic info
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='equity_transactions'
    )
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPES,
        verbose_name="Transaction Type"
    )
    
    # Financial details
    transaction_date = models.DateField(verbose_name="Transaction Date")
    paid_amount_nis = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Amount Paid (NIS)",
        help_text="Actual amount paid by developer"
    )
    approved_amount_nis = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Validated Amount (NIS)",
        help_text="Amount validated by Team Manager (may differ from paid amount)"
    )
    
    # Source tracking (flexible - links to any calculator)
    source_calculator = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Source Calculator",
        help_text="e.g., LandCost_Lines, Suppliers_Lines"
    )
    source_line_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Source Line ID"
    )
    
    # Documentation
    payment_proof = models.FileField(
        upload_to='equity/proofs/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Payment Proof"
    )
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Invoice Number"
    )
    receipt_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Receipt Number"
    )
    check_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Check Number"
    )
    bank_transfer_ref = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Bank Transfer Reference"
    )
    supplier_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Supplier/Payee Name"
    )
    
    # Appraiser workflow
    approval_status = models.CharField(
        max_length=50,
        choices=APPROVAL_STATUS,
        default='DRAFT',
        verbose_name="Approval Status"
    )
    
    # Submitted by Appraiser
    submitted_for_validation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Submitted for Validation Date"
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='equity_submissions',
        verbose_name="Submitted By (Appraiser)"
    )
    
    # Validated by Team Manager
    validated_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Validation Date"
    )
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equity_validations',
        verbose_name="Validated By (Team Manager)"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Rejection/Feedback from Team Manager"
    )
    
    # Notes
    appraiser_notes = models.TextField(
        blank=True,
        verbose_name="Appraiser Notes"
    )
    manager_notes = models.TextField(
        blank=True,
        verbose_name="Team Manager Notes"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Equity Transaction"
        verbose_name_plural = "Equity Transactions"
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['project', 'approval_status']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['submitted_by']),
            models.Index(fields=['validated_by']),
        ]
    
    def __str__(self):
        return f"{self.project} - {self.get_transaction_type_display()} - {self.paid_amount_nis:,.2f} NIS"
    
    def clean(self):
        """Validation logic"""
        # Approved amount cannot exceed paid amount
        if self.approved_amount_nis and self.approved_amount_nis > self.paid_amount_nis:
            raise ValidationError({
                'approved_amount_nis': 'Validated amount cannot exceed paid amount'
            })
    
    def get_equity_value(self):
        """Returns the amount that counts toward equity"""
        if self.approval_status in ['VALIDATED', 'APPROVED_BANK']:
            return self.approved_amount_nis or self.paid_amount_nis
        return Decimal('0')
    
    def can_be_validated_by(self, user):
        """Check if user can validate this transaction"""
        # Only Team Managers can validate
        return user.is_team_manager() or user.is_office_manager()
    
    def submit_for_validation(self, appraiser):
        """Appraiser submits transaction for Team Manager validation"""
        from datetime import date
        self.approval_status = 'PENDING_VALIDATION'
        self.submitted_for_validation_date = date.today()
        self.submitted_by = appraiser
        self.save()
    
    def validate_transaction(self, team_manager, validated_amount=None, notes=''):
        """Team Manager validates transaction"""
        from datetime import date
        self.approval_status = 'VALIDATED'
        self.validated_date = date.today()
        self.validated_by = team_manager
        self.approved_amount_nis = validated_amount or self.paid_amount_nis
        self.manager_notes = notes
        self.save()
    
    def reject_transaction(self, team_manager, reason):
        """Team Manager rejects transaction"""
        from datetime import date
        self.approval_status = 'REJECTED'
        self.validated_date = date.today()
        self.validated_by = team_manager
        self.rejection_reason = reason
        self.save()


class EquitySnapshot(models.Model):
    """Point-in-time equity status - for bank submissions"""
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='equity_snapshots'
    )
    snapshot_date = models.DateField(verbose_name="Snapshot Date")
    
    # Project totals
    total_project_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Total Project Cost"
    )
    required_equity_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Required Equity %"
    )
    required_equity_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Required Equity Amount"
    )
    
    # Equity breakdown
    validated_equity_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Validated Equity Total",
        help_text="All validated transactions by Team Manager"
    )
    pending_validation_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name="Pending Validation Total"
    )
    
    equity_gap = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Equity Gap",
        help_text="Negative = surplus, Positive = deficit"
    )
    equity_gap_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Gap as % of Required"
    )
    
    # Bank submission
    generated_for_bank = models.BooleanField(
        default=False,
        verbose_name="Generated for Bank Submission"
    )
    bank_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Bank Name"
    )
    bank_submission_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Submitted to Bank On"
    )
    
    # Snapshot data (JSON for historical record)
    transactions_snapshot = models.JSONField(
        default=dict,
        verbose_name="Transactions Snapshot",
        help_text="JSON snapshot of all transactions at this point in time"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='equity_snapshots_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Equity Snapshot"
        verbose_name_plural = "Equity Snapshots"
        ordering = ['-snapshot_date', '-created_at']
        indexes = [
            models.Index(fields=['project', 'snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.project} - Snapshot {self.snapshot_date}"
    
    def calculate_gap_percentage(self):
        """Calculate gap as percentage of required equity"""
        if self.required_equity_amount > 0:
            return (self.equity_gap / self.required_equity_amount) * Decimal('100')
        return Decimal('0')
    
    def is_equity_sufficient(self):
        """Check if equity requirement is met"""
        return self.equity_gap <= Decimal('0')


class EquityApprovalHistory(models.Model):
    """Audit trail for equity validations and approvals"""
    
    ACTIONS = [
        ('CREATED', 'Created by Appraiser'),
        ('SUBMITTED', 'Submitted for Validation'),
        ('VALIDATED', 'Validated by Team Manager'),
        ('REJECTED', 'Rejected by Team Manager'),
        ('MODIFIED', 'Modified by Appraiser'),
        ('AMOUNT_CHANGED', 'Validated Amount Changed'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('BANK_APPROVED', 'Approved by Bank'),
    ]
    
    transaction = models.ForeignKey(
        EquityTransaction,
        on_delete=models.CASCADE,
        related_name='approval_history'
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTIONS,
        verbose_name="Action"
    )
    previous_status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Previous Status"
    )
    new_status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="New Status"
    )
    
    previous_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Previous Amount"
    )
    new_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="New Amount"
    )
    
    action_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='equity_actions'
    )
    action_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Equity Approval History"
        verbose_name_plural = "Equity Approval History"
        ordering = ['-action_date']
    
    def __str__(self):
        return f"{self.transaction} - {self.get_action_display()} by {self.action_by}"
