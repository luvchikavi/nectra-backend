"""
Project Expense Tracking Models
"""
from django.db import models
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()


class ProjectExpense(models.Model):
    """Track actual project expenses"""

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'מזומן / Cash'),
        ('CHECK', 'המחאה / Check'),
        ('BANK_TRANSFER', 'העברה בנקאית / Bank Transfer'),
        ('CREDIT_CARD', 'כרטיס אשראי / Credit Card'),
        ('OTHER', 'אחר / Other'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'ממתין לתשלום / Pending'),
        ('PAID', 'שולם / Paid'),
        ('OVERDUE', 'באיחור / Overdue'),
        ('CANCELLED', 'בוטל / Cancelled'),
    ]

    # Project link
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='expenses',
        verbose_name='פרויקט'
    )

    # Expense details
    expense_date = models.DateField(
        verbose_name='תאריך הוצאה',
        help_text='תאריך ביצוע ההוצאה'
    )
    category = models.CharField(
        max_length=200,
        verbose_name='קטגוריה',
        help_text='קטגוריית עלות (מתאימה לתחזית העלויות)'
    )
    item = models.CharField(
        max_length=300,
        verbose_name='סעיף',
        help_text='תיאור הסעיף'
    )
    vendor_name = models.CharField(
        max_length=200,
        verbose_name='ספק/נותן שירות',
        blank=True
    )

    # Amounts
    amount_no_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='סכום ללא מע"מ',
        help_text='הסכום ללא מע"מ'
    )
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=17.0,
        verbose_name='שיעור מע"מ (%)',
        help_text='שיעור המע"מ באחוזים'
    )
    vat_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='סכום מע"מ',
        help_text='סכום המע"מ'
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='סכום כולל',
        help_text='סכום כולל מע"מ'
    )

    # Payment details
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='BANK_TRANSFER',
        verbose_name='אמצעי תשלום'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        verbose_name='סטטוס תשלום'
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='תאריך תשלום בפועל'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='תאריך פירעון'
    )

    # Document tracking
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='מספר חשבונית'
    )
    receipt_file = models.FileField(
        upload_to='expenses/receipts/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='קובץ חשבונית/קבלה'
    )

    # Additional info
    notes = models.TextField(
        blank=True,
        verbose_name='הערות'
    )

    # Tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_expenses',
        verbose_name='נוצר על ידי'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='תאריך יצירה')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='תאריך עדכון')

    class Meta:
        db_table = 'project_expenses'
        verbose_name = 'הוצאת פרויקט'
        verbose_name_plural = 'הוצאות פרויקט'
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['project', 'expense_date']),
            models.Index(fields=['project', 'category']),
            models.Index(fields=['payment_status']),
        ]

    def __str__(self):
        return f"{self.project.project_name} - {self.item} - ₪{self.total_amount:,.0f}"

    def save(self, *args, **kwargs):
        """Auto-calculate VAT and total if not provided"""
        if self.vat_amount is None or self.vat_amount == 0:
            self.vat_amount = self.amount_no_vat * (self.vat_rate / 100)
        if self.total_amount is None or self.total_amount == 0:
            self.total_amount = self.amount_no_vat + self.vat_amount
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        from django.utils import timezone
        if self.payment_status == 'PAID':
            return False
        if self.due_date and self.due_date < timezone.now().date():
            return True
        return False

    @property
    def days_overdue(self):
        """Calculate days overdue"""
        from django.utils import timezone
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days


class ExpenseAttachment(models.Model):
    """Additional attachments for expenses (contracts, receipts, etc.)"""

    expense = models.ForeignKey(
        ProjectExpense,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='הוצאה'
    )
    file = models.FileField(
        upload_to='expenses/attachments/%Y/%m/',
        verbose_name='קובץ'
    )
    file_name = models.CharField(
        max_length=255,
        verbose_name='שם קובץ'
    )
    file_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='סוג קובץ'
    )
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='תיאור'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='תאריך העלאה'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='הועלה על ידי'
    )

    class Meta:
        db_table = 'expense_attachments'
        verbose_name = 'קובץ מצורף להוצאה'
        verbose_name_plural = 'קבצים מצורפים להוצאות'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.expense} - {self.file_name}"
