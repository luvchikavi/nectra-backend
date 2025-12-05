from django.db import models
from datetime import datetime


class Project(models.Model):
    """Main Project model"""
    PHASE_CHOICES = [
        ('PRE_CONSTRUCTION', 'Pre-Construction'),
        ('CONSTRUCTION', 'Construction'),
    ]

    # Israeli Banks
    BANK_CHOICES = [
        ('LEUMI', 'בנק לאומי / Bank Leumi'),
        ('HAPOALIM', 'בנק הפועלים / Bank Hapoalim'),
        ('DISCOUNT', 'בנק דיסקונט / Discount Bank'),
        ('MIZRAHI', 'בנק מזרחי טפחות / Mizrahi-Tefahot Bank'),
        ('INTERNATIONAL', 'הבינלאומי / First International Bank'),
        ('JERUSALEM', 'בנק ירושלים / Bank of Jerusalem'),
        ('MERCANTILE', 'בנק מרכנתיל / Mercantile Discount Bank'),
        ('UNION', 'בנק יהב / Bank Yahav'),
        ('OTSAR_HAHAYAL', 'בנק אוצר החיל / Bank Otsar Ha-Hayal'),
        ('MASSAD', 'בנק מסד / Bank Massad'),
        ('POALEI_AGUDAT', 'בנק פועלי אגודת ישראל / Bank Poalei Agudat Israel'),
        ('OTHER', 'אחר / Other'),
    ]

    # Israeli Cities - 3-letter codes
    CITY_CHOICES = [
        ('TLV', 'תל אביב-יפו / Tel Aviv'),
        ('JRS', 'ירושלים / Jerusalem'),
        ('HFA', 'חיפה / Haifa'),
        ('BSV', 'באר שבע / Beer Sheva'),
        ('RSL', 'ראשון לציון / Rishon LeZion'),
        ('PTH', 'פתח תקווה / Petah Tikva'),
        ('NTN', 'נתניה / Netanya'),
        ('BNB', 'בני ברק / Bnei Brak'),
        ('HLN', 'חולון / Holon'),
        ('RMG', 'רמת גן / Ramat Gan'),
        ('ASD', 'אשדוד / Ashdod'),
        ('RHV', 'רחובות / Rehovot'),
        ('BSM', 'בית שמש / Beit Shemesh'),
        ('KFS', 'כפר סבא / Kfar Saba'),
        ('HRZ', 'הרצליה / Herzliya'),
        ('HDS', 'הוד השרון / Hod HaSharon'),
        ('RMS', 'רמת השרון / Ramat HaSharon'),
        ('ASK', 'אשקלון / Ashkelon'),
        ('RAN', 'רעננה / Ra\'anana'),
        ('LOD', 'לוד / Lod'),
        ('RML', 'רמלה / Ramla'),
        ('NSZ', 'נס ציונה / Ness Ziona'),
        ('MDN', 'מודיעין-מכבים-רעות / Modiin'),
        ('YVN', 'יבנה / Yavne'),
        ('ELT', 'אילת / Eilat'),
        ('TVR', 'טבריה / Tiberias'),
        ('ZFT', 'צפת / Safed'),
        ('AKO', 'עכו / Acre'),
        ('NHR', 'נהריה / Nahariya'),
        ('AFL', 'עפולה / Afula'),
        ('KMZ', 'קריית מוצקין / Kiryat Motzkin'),
        ('KYM', 'קריית ים / Kiryat Yam'),
        ('KTA', 'קריית אתא / Kiryat Ata'),
        ('KBL', 'קריית ביאליק / Kiryat Bialik'),
        ('KRO', 'קריית אונו / Kiryat Ono'),
        ('KGT', 'קריית גת / Kiryat Gat'),
        ('KSM', 'קריית שמונה / Kiryat Shmona'),
        ('GVT', 'גבעתיים / Givatayim'),
        ('GVS', 'גבעת שמואל / Givat Shmuel'),
        ('BTY', 'בת ים / Bat Yam'),
        ('ORY', 'אור יהודה / Or Yehuda'),
        ('YHD', 'יהוד-מונוסון / Yehud'),
        ('ARD', 'ערד / Arad'),
        ('DMN', 'דימונה / Dimona'),
        ('NTV', 'נתיבות / Netivot'),
        ('OFQ', 'אופקים / Ofakim'),
        ('SDR', 'שדרות / Sderot'),
        ('BSN', 'בית שאן / Beit Shean'),
        ('MGD', 'מגדל העמק / Migdal HaEmek'),
        ('NZR', 'נצרת / Nazareth'),
        ('NGL', 'נצרת עילית / Nof HaGalil'),
        ('TKR', 'טירת כרמל / Tirat Carmel'),
        ('HDR', 'חדרה / Hadera'),
        ('KML', 'כרמיאל / Karmiel'),
        ('NSR', 'נשר / Nesher'),
        ('MLT', 'מעלות-תרשיחא / Ma\'alot-Tarshiha'),
        ('MLA', 'מעלה אדומים / Ma\'ale Adumim'),
        ('ARL', 'אריאל / Ariel'),
        ('ELD', 'אלעד / Elad'),
        ('RHT', 'רהט / Rahat'),
        ('ARB', 'עראבה / Ar\'ara'),
        ('ORA', 'אור עקיבא / Or Akiva'),
        ('RSH', 'ראש העין / Rosh HaAyin'),
    ]

    # Basic Info
    city = models.CharField(max_length=3, choices=CITY_CHOICES, verbose_name='עיר / City')
    project_id = models.CharField(max_length=50, unique=True, blank=True, verbose_name='מזהה פרויקט')
    project_name = models.CharField(max_length=200, verbose_name='שם הפרויקט')
    project_description = models.TextField(null=True, blank=True, verbose_name='תיאור הפרויקט')
    phase = models.CharField(
        max_length=20,
        choices=PHASE_CHOICES,
        default='PRE_CONSTRUCTION',
        verbose_name='שלב פרויקט'
    )

    # Soft delete fields
    is_active = models.BooleanField(
        default=True,
        verbose_name='פעיל / Active'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='תאריך מחיקה / Deleted At'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        verbose_name = 'פרויקט'
        verbose_name_plural = 'פרויקטים'

    def save(self, *args, **kwargs):
        if not self.project_id and self.city:
            # Auto-generate project_id: CITY-YEAR-XXXX format
            now = datetime.now()
            year = now.strftime('%Y')

            # Find the last project created for this city this year
            prefix = f"{self.city}-{year}-"
            last_project = Project.objects.filter(
                project_id__startswith=prefix
            ).order_by('-project_id').first()

            if last_project:
                # Extract the number and increment
                last_num = int(last_project.project_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.project_id = f"{prefix}{new_num:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.project_name

    def soft_delete(self):
        """Soft delete the project - marks as inactive but keeps data"""
        from django.utils import timezone
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft-deleted project"""
        self.is_active = True
        self.deleted_at = None
        self.save()

    @classmethod
    def active_projects(cls):
        """Get only active projects"""
        return cls.objects.filter(is_active=True)


class ProjectDataInputs(models.Model):
    """Stores all data inputs for Phase 1 (Pre-Construction)"""
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='data_inputs',
        verbose_name='פרויקט'
    )

    # Item 4: Property Details (table with multiple parcels)
    property_details = models.JSONField(null=True, blank=True, verbose_name='פרטי נכס')
    # Format: [{"rights": "", "block": "", "plot": "", "area_cell": "", "main_plan": "", "land_area": 0, "designation": ""}]

    # Item 5: Dates
    dates = models.JSONField(null=True, blank=True, verbose_name='תאריכים')
    # Format: {
    #   "excavation_permit_date": "YYYY-MM-DD",
    #   "excavation_start_date": "YYYY-MM-DD",
    #   "construction_permit_date": "YYYY-MM-DD",
    #   "construction_start_date": "YYYY-MM-DD",
    #   "construction_duration_months": 24
    # }

    # Item 6: Developer Details
    developer = models.JSONField(null=True, blank=True, verbose_name='פרטי יזם')
    # Format: {
    #   "company_name": "",
    #   "company_number": "",
    #   "contacts": [{"role": "", "name": "", "phone": "", "email": ""}]
    # }

    # Item 7: Financing/Bank Details
    financing = models.JSONField(null=True, blank=True, verbose_name='פרטי מימון')
    # Format: {
    #   "financing_body_name": "",
    #   "type": "BANKING" or "NON_BANKING",
    #   "contacts": [{"role": "", "name": "", "phone": "", "email": ""}]
    # }

    # Item 8: Profitability (auto-calculated)
    profitability = models.JSONField(null=True, blank=True, verbose_name='רווחיות')

    # Item 9: Land Value / Zero Report (auto-calculated)
    land_value = models.JSONField(null=True, blank=True, verbose_name='ערך קרקע / דוח אפס')
    # Format: {
    #   "total_income_residential_with_vat": 0,
    #   "total_income_commercial_no_vat": 0,
    #   "total_income_combined_no_vat": 0,
    #   "total_income_minus_developer_rate": 0,
    #   "total_cost_project": 0,
    #   "land_cost_balance": 0
    # }

    # Item 10: Fixed Rates
    fixed_rates = models.JSONField(null=True, blank=True, verbose_name='שיעורים קבועים')
    # Format: {
    #   "consumer_price_index": 102.6,
    #   "construction_input_index": 121.5,
    #   "developer_profitability_rate": 15.0,
    #   "vat_rate": 18.0
    # }

    # Item 11: Insurance (table)
    insurance = models.JSONField(null=True, blank=True, verbose_name='ביטוח')
    # Format: [{"component": "", "amount_no_vat": 0, "total_insurance": 0}]

    # Item 12: Construction Classification
    construction_classification = models.JSONField(null=True, blank=True, verbose_name='סיווג בנייה')
    # Format: {
    #   "total_sqm_project": 0,
    #   "total_sqm_permit": 0,
    #   "total_sqm_construction": 0,
    #   "direct_construction_cost": 0,
    #   "classification_needed": ""
    # }

    # Item 13: Guarantees (table)
    guarantees = models.JSONField(null=True, blank=True, verbose_name='ערבויות')
    # Format: [{"guarantee_type": "", "amount_no_vat": 0}]

    # Item 14: Sensitivity Analysis
    sensitivity_analysis = models.JSONField(null=True, blank=True, verbose_name='ניתוח רגישות')
    # Format: {
    #   "base": {"income": 0, "cost": 0, "profit": 0},
    #   "cost_increase": {"percent": 5, "income": 0, "cost": 0, "profit": 0},
    #   "income_decrease": {"percent": 5, "income": 0, "cost": 0, "profit": 0},
    #   "combined": {"income_percent": -5, "cost_percent": 5, "income": 0, "cost": 0, "profit": 0}
    # }

    # Items 15-17: To be added later (Monthly Cash Flow, Income Projection, Cost Projection)
    monthly_cashflow = models.JSONField(null=True, blank=True, verbose_name='תזרים מזומנים חודשי')
    revenue_forecast = models.JSONField(null=True, blank=True, verbose_name='תחזית הכנסות')
    cost_forecast = models.JSONField(null=True, blank=True, verbose_name='תחזית עלויות')

    # Legacy fields (keep for backward compatibility)
    project_description_text = models.TextField(null=True, blank=True, verbose_name='תיאור פרויקט - טקסט')
    project_description_table = models.JSONField(null=True, blank=True, verbose_name='תיאור פרויקט - טבלה')
    timeline_dates = models.JSONField(null=True, blank=True, verbose_name='לוחות זמנים')
    sales_timeline = models.JSONField(null=True, blank=True, verbose_name='לוח מכירות')
    break_even = models.JSONField(null=True, blank=True, verbose_name='נקודת איזון')
    index_values = models.JSONField(null=True, blank=True, verbose_name='מדדים')
    cashflow = models.JSONField(null=True, blank=True, verbose_name='תזרים מזומנים')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_data_inputs'
        verbose_name = 'נתוני קלט פרויקט'
        verbose_name_plural = 'נתוני קלט פרויקטים'

    def __str__(self):
        return f"Data Inputs for {self.project.project_name}"


# Import expense models
from .models_expenses import ProjectExpense, ExpenseAttachment


class BankTransaction(models.Model):
    """Model for storing bank transactions from monthly statements"""

    TRANSACTION_STATUS = [
        ('PENDING', 'ממתין / Pending'),
        ('APPROVED', 'מאושר / Approved'),
        ('REJECTED', 'נדחה / Rejected'),
    ]

    TRANSACTION_TYPE = [
        ('DEBIT', 'חובה / Debit'),
        ('CREDIT', 'זכות / Credit'),
    ]

    # Transaction categories for financial execution tracking
    CATEGORY_CHOICES = [
        ('PURCHASE_RECEIPTS', 'קבלות רכישה / Purchase Receipts'),
        ('LOANS', 'הלוואות / Loans'),
        ('OWNER_EQUITY', 'הון עצמי / Owner Equity'),
        ('BANK_FEES', 'עמלות בנק / Bank Fees'),
        ('TAX_PAYMENTS', 'תשלומי מס / Tax Payments'),
        ('CONTRACTOR_PAYMENTS', 'תשלומים לקבלנים / Contractor Payments'),
        ('SUPPLIER_PAYMENTS', 'תשלומים לספקים / Supplier Payments'),
        ('PROFESSIONAL_FEES', 'שכר טרחה מקצועית / Professional Fees'),
        ('INSURANCE', 'ביטוח / Insurance'),
        ('PERMITS_FEES', 'אגרות והיתרים / Permits & Fees'),
        ('MARKETING', 'שיווק / Marketing'),
        ('SALES_INCOME', 'הכנסות ממכירות / Sales Income'),
        ('REFUNDS', 'החזרים / Refunds'),
        ('OTHER_INCOME', 'הכנסות אחרות / Other Income'),
        ('OTHER_EXPENSE', 'הוצאות אחרות / Other Expenses'),
    ]

    # Foreign key to project
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='bank_transactions',
        verbose_name='פרויקט'
    )

    # Bank information
    bank = models.CharField(
        max_length=50,
        choices=Project.BANK_CHOICES,
        verbose_name='בנק'
    )
    account_number = models.CharField(max_length=50, null=True, blank=True, verbose_name='מספר חשבון')

    # Transaction details
    transaction_date = models.DateField(verbose_name='תאריך תנועה')
    value_date = models.DateField(null=True, blank=True, verbose_name='יום ערך')
    description = models.TextField(verbose_name='תיאור התנועה')
    reference_number = models.CharField(max_length=100, null=True, blank=True, verbose_name='אסמכתא')

    # Amounts
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE,
        verbose_name='סוג תנועה'
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='סכום')
    balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='יתרה')

    # Approval workflow
    status = models.CharField(
        max_length=20,
        choices=TRANSACTION_STATUS,
        default='PENDING',
        verbose_name='סטטוס'
    )
    approval_notes = models.TextField(null=True, blank=True, verbose_name='הערות אישור')
    approved_by = models.CharField(max_length=100, null=True, blank=True, verbose_name='אושר על ידי')
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name='תאריך אישור')

    # Categorization
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        verbose_name='קטגוריה'
    )
    is_construction_related = models.BooleanField(default=False, verbose_name='קשור לבנייה')
    meets_plan = models.BooleanField(default=False, verbose_name='עומד בתוכנית')
    meets_construction_stage = models.BooleanField(default=False, verbose_name='עומד בשלב בנייה')

    # File upload reference
    uploaded_file = models.CharField(max_length=500, null=True, blank=True, verbose_name='קובץ מקור')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bank_transactions'
        verbose_name = 'תנועת בנק'
        verbose_name_plural = 'תנועות בנק'
        ordering = ['-transaction_date', '-id']
        indexes = [
            models.Index(fields=['project', 'transaction_date']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['bank', 'account_number']),
        ]

    def __str__(self):
        return f"{self.bank} - {self.transaction_date} - ₪{self.amount}"


class ConstructionProgress(models.Model):
    """Model for storing construction progress plan and current state"""

    # Foreign key to project
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='construction_progress',
        verbose_name='פרויקט'
    )

    # Contract information
    total_contract_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='סכום חוזה כולל'
    )

    # Available floors for this project
    # Example: ["כללי", "-2", "-1", "קרקע", "1", "2", "3", "4", "5", "6", "7", "8", "גג"]
    available_floors = models.JSONField(
        default=list,
        verbose_name='קומות זמינות'
    )

    # Construction tasks with progress tracking
    # Stores the complete table structure from Excel
    tasks = models.JSONField(
        default=list,
        verbose_name='משימות בנייה'
    )
    # Format:
    # [
    #   {
    #     "task_number": 1,
    #     "chapter": "שלד",
    #     "chapter_weight": 0.4144,
    #     "work_item": "התארגנות",
    #     "percent_of_chapter": 0.01,
    #     "percent_of_total": 0.00414,
    #     "budgeted_amount": 136966.00,
    #     "floor_progress": {
    #       "כללי": 1.0,
    #       "-2": 0,
    #       "-1": 0,
    #       "קרקע": 0,
    #       "1": 0,
    #       ...
    #     },
    #     "total_completion": 1.0,
    #     "completion_rate": 0.00414,
    #     "actual_amount": 136966.00,
    #     "previous_month_progress": 0.9,
    #     "monthly_delta": 127647.90
    #   },
    #   ...
    # ]

    # Overall progress summary
    overall_completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='אחוז השלמה כולל'
    )
    total_spent_to_date = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='סכום שהוצא עד היום'
    )

    # Upload tracking
    original_file_name = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='שם קובץ מקורי'
    )
    uploaded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='תאריך העלאה'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'construction_progress'
        verbose_name = 'התקדמות בנייה'
        verbose_name_plural = 'התקדמות בנייה'

    def __str__(self):
        return f"Construction Progress - {self.project.project_name}"


class ConstructionProgressSnapshot(models.Model):
    """Model for storing monthly snapshots of construction progress"""

    # Foreign key to project
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='progress_snapshots',
        verbose_name='פרויקט'
    )

    # Snapshot date
    snapshot_date = models.DateField(verbose_name='תאריך צילום')
    month = models.IntegerField(verbose_name='חודש')  # 1-12
    year = models.IntegerField(verbose_name='שנה')

    # Snapshot of tasks at this point in time
    tasks_snapshot = models.JSONField(
        verbose_name='צילום משימות'
    )

    # Summary at time of snapshot
    overall_completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='אחוז השלמה כולל'
    )
    total_spent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='סכום שהוצא'
    )

    # Notes from employee
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='הערות'
    )

    # Metadata
    created_by = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='נוצר על ידי'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'construction_progress_snapshots'
        verbose_name = 'צילום התקדמות'
        verbose_name_plural = 'צילומי התקדמות'
        ordering = ['-snapshot_date', '-id']
        unique_together = ['project', 'year', 'month']
        indexes = [
            models.Index(fields=['project', 'snapshot_date']),
            models.Index(fields=['project', 'year', 'month']),
        ]

    def __str__(self):
        return f"{self.project.project_name} - {self.year}/{self.month:02d}"


class EquityDeposit(models.Model):
    """Model for tracking equity deposits for a project"""

    SOURCE_CHOICES = [
        ('MANUAL', 'הזנה ידנית / Manual Entry'),
        ('TRANSFER', 'העברה בנקאית / Bank Transfer'),
        ('CHECK', 'צ\'ק / Check'),
        ('CASH', 'מזומן / Cash'),
        ('BANK_TRANSACTION', 'תנועת בנק / Bank Transaction'),
        ('OTHER', 'אחר / Other'),
    ]

    # Foreign key to project
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='equity_deposits',
        verbose_name='פרויקט'
    )

    # Deposit details
    deposit_date = models.DateField(verbose_name='תאריך הפקדה')
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='סכום'
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='MANUAL',
        verbose_name='מקור'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='תיאור'
    )
    reference_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='אסמכתא'
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='הערות'
    )

    # Link to bank transaction if applicable
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equity_deposits',
        verbose_name='תנועת בנק מקושרת'
    )

    # Metadata
    created_by = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='נוצר על ידי'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equity_deposits'
        verbose_name = 'הפקדת הון עצמי'
        verbose_name_plural = 'הפקדות הון עצמי'
        ordering = ['-deposit_date', '-id']
        indexes = [
            models.Index(fields=['project', 'deposit_date']),
        ]

    def __str__(self):
        return f"{self.project.project_name} - ₪{self.amount} - {self.deposit_date}"


class ProjectDocument(models.Model):
    """Model for storing project-related documents"""

    CATEGORY_CHOICES = [
        ('CONTRACT', 'חוזה / Contract'),
        ('PERMIT', 'היתר / Permit'),
        ('PLAN', 'תכנית / Plan'),
        ('REPORT', 'דוח / Report'),
        ('INVOICE', 'חשבונית / Invoice'),
        ('BANK', 'בנק / Bank'),
        ('LEGAL', 'משפטי / Legal'),
        ('INSURANCE', 'ביטוח / Insurance'),
        ('ARCHITECT', 'אדריכלות / Architecture'),
        ('ENGINEERING', 'הנדסה / Engineering'),
        ('MARKETING', 'שיווק / Marketing'),
        ('PHOTOS', 'תמונות / Photos'),
        ('OTHER', 'אחר / Other'),
    ]

    # Foreign key to project
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='פרויקט'
    )

    # Document details
    name = models.CharField(max_length=255, verbose_name='שם המסמך')
    description = models.TextField(null=True, blank=True, verbose_name='תיאור')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='OTHER',
        verbose_name='קטגוריה'
    )

    # File storage
    file = models.FileField(
        upload_to='project_documents/%Y/%m/',
        verbose_name='קובץ'
    )
    file_name = models.CharField(max_length=255, verbose_name='שם קובץ מקורי')
    file_size = models.IntegerField(verbose_name='גודל קובץ (בבתים)')
    file_type = models.CharField(max_length=100, verbose_name='סוג קובץ')

    # Optional date for the document
    document_date = models.DateField(null=True, blank=True, verbose_name='תאריך מסמך')

    # Tags for better searchability
    tags = models.JSONField(default=list, blank=True, verbose_name='תגיות')

    # Metadata
    uploaded_by = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='הועלה על ידי'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_documents'
        verbose_name = 'מסמך פרויקט'
        verbose_name_plural = 'מסמכי פרויקט'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'category']),
            models.Index(fields=['project', 'created_at']),
        ]

    def __str__(self):
        return f"{self.project.project_name} - {self.name}"


class ProjectChange(models.Model):
    """Model for tracking project changes (budget, income, cost, duration, financing)"""

    CHANGE_TYPE_CHOICES = [
        ('INCOME', 'הכנסה / Income'),
        ('COST', 'עלות / Cost'),
        ('DURATION', 'משך זמן / Duration'),
        ('BUDGET', 'תקציב / Budget'),
        ('FINANCING', 'מימון / Financing'),
        ('SCOPE', 'היקף / Scope'),
        ('OTHER', 'אחר / Other'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'טיוטה / Draft'),
        ('PENDING', 'ממתין לאישור / Pending Approval'),
        ('APPROVED', 'מאושר / Approved'),
        ('REJECTED', 'נדחה / Rejected'),
        ('IMPLEMENTED', 'יושם / Implemented'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'נמוך / Low'),
        ('MEDIUM', 'בינוני / Medium'),
        ('HIGH', 'גבוה / High'),
        ('CRITICAL', 'קריטי / Critical'),
    ]

    # Foreign key to project
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='changes',
        verbose_name='פרויקט'
    )

    # Change identification
    change_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name='מספר שינוי'
    )
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES,
        verbose_name='סוג שינוי'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='כותרת'
    )
    description = models.TextField(
        verbose_name='תיאור השינוי'
    )

    # Financial impact
    original_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='ערך מקורי'
    )
    requested_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='ערך מבוקש'
    )
    approved_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='ערך מאושר'
    )
    impact_on_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='השפעה על התקציב'
    )

    # Duration changes (for DURATION type)
    original_duration_months = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='משך זמן מקורי (חודשים)'
    )
    requested_duration_months = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='משך זמן מבוקש (חודשים)'
    )
    approved_duration_months = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='משך זמן מאושר (חודשים)'
    )

    # Status and workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name='סטטוס'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        verbose_name='עדיפות'
    )

    # Bank approval
    bank_approval_required = models.BooleanField(
        default=False,
        verbose_name='נדרש אישור בנק'
    )
    bank_approved = models.BooleanField(
        default=False,
        verbose_name='אושר על ידי הבנק'
    )
    bank_approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='תאריך אישור הבנק'
    )
    bank_approval_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='הערות אישור הבנק'
    )

    # Approval workflow
    requested_by = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='מבקש השינוי'
    )
    requested_date = models.DateField(
        auto_now_add=True,
        verbose_name='תאריך בקשה'
    )
    approved_by = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='מאשר השינוי'
    )
    approved_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='תאריך אישור'
    )
    rejection_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name='סיבת דחייה'
    )

    # Implementation tracking
    implemented_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='תאריך יישום'
    )
    implementation_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='הערות יישום'
    )

    # Attachments and references
    related_documents = models.JSONField(
        default=list,
        blank=True,
        verbose_name='מסמכים קשורים'
    )
    affected_budget_items = models.JSONField(
        default=list,
        blank=True,
        verbose_name='סעיפי תקציב מושפעים'
    )

    # Metadata
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='הערות'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_changes'
        verbose_name = 'שינוי פרויקט'
        verbose_name_plural = 'שינויי פרויקט'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'change_type']),
            models.Index(fields=['project', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.change_number:
            # Auto-generate change number: CHG-PROJECTID-XXXX format
            prefix = f"CHG-{self.project.project_id}-"
            last_change = ProjectChange.objects.filter(
                change_number__startswith=prefix
            ).order_by('-change_number').first()

            if last_change:
                last_num = int(last_change.change_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1

            self.change_number = f"{prefix}{new_num:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.change_number} - {self.title}"

    @property
    def value_difference(self):
        """Calculate the difference between original and approved/requested value"""
        compare_value = self.approved_value if self.approved_value else self.requested_value
        if self.original_value and compare_value:
            return compare_value - self.original_value
        return None

    @property
    def duration_difference(self):
        """Calculate the difference in duration months"""
        compare_duration = self.approved_duration_months if self.approved_duration_months else self.requested_duration_months
        if self.original_duration_months and compare_duration:
            return compare_duration - self.original_duration_months
        return None
