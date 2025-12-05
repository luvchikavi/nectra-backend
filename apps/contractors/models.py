"""
Contractor Module Models
Handles contractor management, invoice uploads, OCR processing, and approval workflow
"""
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


# ============================================================================
# CONTRACTOR
# ============================================================================

class Contractor(models.Model):
    """Contractor profile linked to a user account"""

    # Link to user for authentication
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='contractor_profile',
        verbose_name="משתמש / User"
    )

    # Company Information
    company_name = models.CharField(
        max_length=200,
        verbose_name="שם חברה / Company Name"
    )
    tax_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ח.פ / עוסק מורשה / Tax ID"
    )

    # Contact Information
    contact_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="איש קשר / Contact Name"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="טלפון / Phone"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="אימייל / Email"
    )
    address = models.TextField(
        blank=True,
        verbose_name="כתובת / Address"
    )

    # Projects this contractor can access (Many-to-Many)
    projects = models.ManyToManyField(
        'projects.Project',
        related_name='contractors',
        blank=True,
        verbose_name="פרויקטים / Projects"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name="פעיל / Active"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contractors'
        verbose_name = 'Contractor'
        verbose_name_plural = 'Contractors'
        ordering = ['company_name']

    def __str__(self):
        return f"{self.company_name} ({self.tax_id})"


# ============================================================================
# INVOICE
# ============================================================================

class Invoice(models.Model):
    """Invoice uploaded by contractor"""

    INVOICE_STATUS = [
        ('PENDING_OCR', 'ממתין לעיבוד / Pending OCR'),
        ('OCR_FAILED', 'עיבוד נכשל / OCR Failed'),
        ('PENDING_REVIEW', 'ממתין לאישור / Pending Review'),
        ('APPROVED', 'מאושר / Approved'),
        ('REJECTED', 'נדחה / Rejected'),
        ('PAID', 'שולם / Paid'),
    ]

    INVOICE_CATEGORIES = [
        ('DIRECT_BUILDING', 'בנייה ישירה / Direct Building'),
        ('CONSULTING', 'ייעוץ / Consulting'),
        ('PLANNING', 'תכנון / Planning & Architecture'),
        ('SUPERVISION', 'פיקוח / Supervision'),
        ('MATERIALS', 'חומרים / Materials'),
        ('EQUIPMENT', 'ציוד / Equipment'),
        ('LABOR', 'עבודה / Labor'),
        ('SUBCONTRACTOR', 'קבלן משנה / Subcontractor'),
        ('TAXES', 'מיסים / Taxes'),
        ('FEES', 'אגרות / Fees & Permits'),
        ('INSURANCE', 'ביטוח / Insurance'),
        ('LEGAL', 'משפטי / Legal'),
        ('MARKETING', 'שיווק / Marketing'),
        ('FINANCE', 'מימון / Finance Costs'),
        ('GENERAL', 'הוצאות כלליות / General Expenses'),
        ('OTHER', 'אחר / Other'),
    ]

    # Links
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name="קבלן / Contractor",
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='contractor_invoices',
        verbose_name="פרויקט / Project"
    )

    # Invoice Details (from OCR or manual entry)
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="מספר חשבונית / Invoice Number"
    )
    invoice_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="תאריך חשבונית / Invoice Date"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="תאריך לתשלום / Due Date"
    )

    # Vendor Details (extracted from invoice)
    vendor_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="שם ספק / Vendor Name"
    )
    vendor_tax_id = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="ח.פ ספק / Vendor Tax ID"
    )

    # Amounts
    net_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="סכום לפני מע\"מ / Net Amount"
    )
    vat_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="מע\"מ / VAT Amount"
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="סכום כולל / Total Amount"
    )

    # Categorization
    category = models.CharField(
        max_length=30,
        choices=INVOICE_CATEGORIES,
        blank=True,
        verbose_name="קטגוריה / Category"
    )

    # Link to Construction Progress (optional)
    construction_progress = models.ForeignKey(
        'projects.ConstructionProgress',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name="סעיף התקדמות בנייה / Construction Progress Item"
    )

    # Link to Bank Transaction (for matching)
    bank_transaction = models.ForeignKey(
        'projects.BankTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matched_invoices',
        verbose_name="תנועת בנק / Bank Transaction"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS,
        default='PENDING_OCR',
        verbose_name="סטטוס / Status"
    )

    # File Storage
    original_file = models.FileField(
        upload_to='invoices/%Y/%m/',
        verbose_name="קובץ מקורי / Original File",
        null=True,
        blank=True
    )

    # OCR Data (stored as JSON)
    ocr_raw_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="נתוני OCR גולמיים / Raw OCR Data"
    )
    ocr_confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="רמת ביטחון OCR / OCR Confidence"
    )

    # Notes
    description = models.TextField(
        blank=True,
        verbose_name="תיאור / Description"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="הערות / Notes"
    )

    # Metadata
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_invoices',
        verbose_name="הועלה על ידי / Uploaded By"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contractor_invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number or 'No Number'} - {self.vendor_name or self.contractor.company_name}"

    @property
    def is_pending_approval(self):
        return self.status == 'PENDING_REVIEW'

    @property
    def is_approved(self):
        return self.status in ['APPROVED', 'PAID']

    @property
    def can_be_edited(self):
        """Can only edit if not yet approved"""
        return self.status in ['PENDING_OCR', 'OCR_FAILED', 'PENDING_REVIEW']


# ============================================================================
# INVOICE APPROVAL
# ============================================================================

class InvoiceApproval(models.Model):
    """Approval/Rejection record for invoices"""

    APPROVAL_ACTIONS = [
        ('APPROVE', 'אישור / Approve'),
        ('REJECT', 'דחייה / Reject'),
        ('REQUEST_CHANGES', 'בקשת שינויים / Request Changes'),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='approvals',
        verbose_name="חשבונית / Invoice"
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='invoice_approvals',
        verbose_name="מאשר / Approved By"
    )

    action = models.CharField(
        max_length=20,
        choices=APPROVAL_ACTIONS,
        verbose_name="פעולה / Action"
    )

    comments = models.TextField(
        blank=True,
        verbose_name="הערות / Comments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoice_approvals'
        verbose_name = 'Invoice Approval'
        verbose_name_plural = 'Invoice Approvals'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice} - {self.get_action_display()} by {self.approved_by}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update invoice status based on action
        if self.action == 'APPROVE':
            self.invoice.status = 'APPROVED'
            self.invoice.save()
        elif self.action == 'REJECT':
            self.invoice.status = 'REJECTED'
            self.invoice.save()


# ============================================================================
# ACTUAL COSTS (Aggregated from approved invoices)
# ============================================================================

class ActualCost(models.Model):
    """
    Actual costs tracking - aggregated from approved invoices
    Separate from forecast costs (Section 8)
    """

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='actual_costs',
        verbose_name="פרויקט / Project"
    )

    # Period
    year = models.IntegerField(verbose_name="שנה / Year")
    month = models.IntegerField(verbose_name="חודש / Month")

    # Category totals
    category = models.CharField(
        max_length=30,
        choices=Invoice.INVOICE_CATEGORIES,
        verbose_name="קטגוריה / Category"
    )

    # Amounts
    total_net = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="סה\"כ לפני מע\"מ / Total Net"
    )
    total_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="סה\"כ מע\"מ / Total VAT"
    )
    total_gross = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="סה\"כ כולל / Total Gross"
    )

    # Invoice count
    invoice_count = models.IntegerField(
        default=0,
        verbose_name="מספר חשבוניות / Invoice Count"
    )

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'actual_costs'
        verbose_name = 'Actual Cost'
        verbose_name_plural = 'Actual Costs'
        ordering = ['-year', '-month', 'category']
        unique_together = [['project', 'year', 'month', 'category']]

    def __str__(self):
        return f"{self.project} - {self.year}/{self.month} - {self.get_category_display()}"

    @classmethod
    def recalculate_for_project(cls, project_id, year, month):
        """Recalculate actual costs from approved invoices"""
        from django.db.models import Sum, Count

        # Get all approved invoices for this project/period
        invoices = Invoice.objects.filter(
            project_id=project_id,
            status__in=['APPROVED', 'PAID'],
            invoice_date__year=year,
            invoice_date__month=month
        ).exclude(category='')

        # Group by category and aggregate
        aggregates = invoices.values('category').annotate(
            total_net=Sum('net_amount'),
            total_vat=Sum('vat_amount'),
            total_gross=Sum('total_amount'),
            count=Count('id')
        )

        # Update or create ActualCost records
        for agg in aggregates:
            cls.objects.update_or_create(
                project_id=project_id,
                year=year,
                month=month,
                category=agg['category'],
                defaults={
                    'total_net': agg['total_net'] or 0,
                    'total_vat': agg['total_vat'] or 0,
                    'total_gross': agg['total_gross'] or 0,
                    'invoice_count': agg['count']
                }
            )
