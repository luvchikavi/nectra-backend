"""
Sales & Income Models
Tracks apartment inventory, sales, payments, and revenue forecasting
"""
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


# ============================================================================
# CUSTOMER
# ============================================================================

class Customer(models.Model):
    """Customer/Buyer information"""

    CUSTOMER_TYPES = [
        ('BUYER', 'רוכש רגיל / Regular Buyer'),
        ('OWNER', 'בעל דירה / Property Owner'),
        ('INVESTOR', 'משקיע / Investor'),
        ('TENANT', 'שוכר / Tenant'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=100, verbose_name="שם פרטי / First Name")
    last_name = models.CharField(max_length=100, verbose_name="שם משפחה / Last Name")
    id_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ת.ז / ID Number"
    )

    # Contact Information
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

    # Customer Type
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='BUYER',
        verbose_name="סוג לקוח / Customer Type"
    )

    # Additional Information
    notes = models.TextField(
        blank=True,
        verbose_name="הערות / Notes"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ============================================================================
# APARTMENT INVENTORY
# ============================================================================

class ApartmentInventory(models.Model):
    """Complete apartment inventory with sales tracking"""

    UNIT_TYPES = [
        # Residential
        ('APARTMENT', 'דירה / Apartment'),
        ('PENTHOUSE', 'פנטהאוז / Penthouse'),
        ('GARDEN', 'גן / Garden Apartment'),
        ('DUPLEX', 'דופלקס / Duplex'),
        ('MINI_PENTHOUSE', 'מיני פנטהאוז / Mini Penthouse'),
        # Commercial
        ('OFFICE', 'משרדים / Office'),
        ('RETAIL', 'מסחר / Retail'),
        ('STORAGE', 'מחסן / Storage'),
        ('WAREHOUSE', 'מחסן / Warehouse'),
        ('INDUSTRIAL', 'תעשיה / Industrial'),
        ('LIGHT_INDUSTRIAL', 'תעשיה קלה / Light Industrial'),
        ('HALL', 'אולם / Hall'),
        ('LOGISTICS', 'לוגיסטיקה / Logistics'),
        # Parking
        ('PARKING_REGULAR', 'חניה רגילה / Regular Parking'),
        ('PARKING_TANDEM', 'חניה טורקית / Tandem Parking'),
        ('PARKING_UNDERGROUND', 'חניה תת קרקעית / Underground Parking'),
        ('PARKING_ELEVATED', 'חניה עילית / Elevated Parking'),
        # Other
        ('OTHER', 'אחר / Other'),
    ]

    UNIT_STATUS = [
        ('FOR_SALE', 'לשיווק / For Sale'),
        ('SOLD', 'נמכר / Sold'),
        ('COMPENSATION', 'תמורה / Compensation'),
        ('FOR_RENT', 'להשכרה / For Rent'),
        ('RESERVED', 'שמור / Reserved'),
        ('IN_PROCESS', 'בהליכים / In Process'),
        ('UNAVAILABLE', 'לא זמין / Unavailable'),
    ]
    
    # Basic Information
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='apartments'
    )
    building_number = models.CharField(
        max_length=10,
        verbose_name="בניין / Building Number"
    )
    wing = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="אגף / Wing"
    )
    floor = models.IntegerField(verbose_name="קומה / Floor Number")
    unit_number = models.CharField(
        max_length=20,
        verbose_name="מס' / Unit Number"
    )
    plan_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="מס' עפ\"י תכנית בקשה / Plan Number"
    )
    unit_unique_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Unit Unique ID"
    )

    # Unit Characteristics
    unit_type = models.CharField(
        max_length=30,
        choices=UNIT_TYPES,
        default='APARTMENT',
        verbose_name="סוג נכס / Unit Type"
    )
    unit_sub_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="סוג משני / Sub Type"
    )
    room_count = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="חדרים / Room Count"
    )
    unit_direction = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="כיוון / Unit Direction"
    )

    # Areas
    net_area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="שטח נטו במ\"ר / Net Area (sqm)"
    )
    gross_area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="שטח ברוטו במ\"ר / Gross Area (sqm)"
    )
    unit_area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="שטח פלדלת במ\"ר / Unit Area (sqm)"
    )
    balcony_area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="מרפסת שמש במ\"ר / Balcony Area (sqm)"
    )
    terrace_area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="מרפסת במ\"ר / Terrace Area (sqm)"
    )
    roof_terrace_area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="מרפסת גג במ\"ר / Roof Terrace Area (sqm)"
    )
    yard_area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="חצר במ\"ר / Yard Area (sqm)"
    )
    gallery_area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="גלריה במ\"ר / Gallery Area (sqm)"
    )

    # Parking and Storage
    parking_spaces = models.IntegerField(
        default=0,
        verbose_name="חניות / Parking Spaces"
    )
    storage_count = models.IntegerField(
        default=0,
        verbose_name="מחסנים / Storage Count"
    )
    
    # Pricing
    price_per_sqm_equivalent_with_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="שווי למ\"ר אקוו' כולל מע\"מ / Price per sqm Equivalent (with VAT)"
    )
    price_per_sqm_net_with_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="שווי למ\"ר פלדלת כולל מע\"מ / Price per sqm Net (with VAT)"
    )
    price_per_sqm_no_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="שווי למ\"ר לא כולל מע\"מ / Price per sqm (No VAT)"
    )
    list_price_with_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="שווי כולל מע\"מ / List Price (with VAT)"
    )
    list_price_no_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="שווי ללא מע\"מ / List Price (No VAT)"
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="הנחה % / Discount Percent"
    )
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="הנחה סכום / Discount Amount"
    )
    final_price_with_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="מחיר סופי כולל מע\"מ / Final Price (with VAT)"
    )
    final_price_no_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="מחיר סופי ללא מע\"מ / Final Price (No VAT)"
    )
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.17,
        verbose_name="מע\"מ / VAT Rate"
    )

    # Sale Status
    unit_status = models.CharField(
        max_length=20,
        choices=UNIT_STATUS,
        default='FOR_SALE',
        verbose_name="סטטוס / Status"
    )
    contract_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="תאריך חוזה / Contract Date"
    )
    expected_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="תאריך מסירה / Expected Delivery Date"
    )

    # Customer Information (Link to Customer model)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='apartments',
        verbose_name="לקוח / Customer"
    )
    # Legacy fields (kept for backward compatibility and quick display)
    customer_first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="שם פרטי / First Name"
    )
    customer_last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="שם משפחה / Last Name"
    )
    sell_contract = models.FileField(
        upload_to='contracts/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="חוזה / Sell Contract"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'apartment_inventory'
        verbose_name = 'Apartment'
        verbose_name_plural = 'Apartment Inventory'
        ordering = ['building_number', 'floor', 'unit_number']
        unique_together = [['project', 'building_number', 'floor', 'unit_number']]

    def __str__(self):
        return f"{self.unit_unique_id} - {self.get_unit_type_display()}"

    def save(self, *args, **kwargs):
        # Auto-generate unique ID if not provided
        if not self.unit_unique_id:
            wing_part = f"-{self.wing}" if self.wing else ""
            self.unit_unique_id = f"P{self.project.id}-B{self.building_number}{wing_part}-F{self.floor}-U{self.unit_number}"

        # Calculate final prices if discount is applied
        if self.list_price_with_vat:
            if self.discount_percent > 0:
                discount = self.list_price_with_vat * (self.discount_percent / 100)
                self.discount_amount = discount
                self.final_price_with_vat = self.list_price_with_vat - discount
            elif self.discount_amount > 0:
                self.final_price_with_vat = self.list_price_with_vat - self.discount_amount
            else:
                self.final_price_with_vat = self.list_price_with_vat

        super().save(*args, **kwargs)

    def calculate_final_price_with_vat(self):
        """Calculate final price including VAT"""
        if self.final_price_with_vat:
            return self.final_price_with_vat
        if self.final_price_no_vat:
            return self.final_price_no_vat * (1 + self.vat_rate)
        if self.list_price_with_vat:
            return self.list_price_with_vat
        if self.list_price_no_vat:
            return self.list_price_no_vat * (1 + self.vat_rate)
        return Decimal('0')

    def total_area(self):
        """Calculate total area including all spaces"""
        total = Decimal('0')
        if self.unit_area_sqm:
            total += self.unit_area_sqm
        if self.net_area_sqm:
            total += self.net_area_sqm
        total += (self.balcony_area_sqm + self.terrace_area_sqm +
                  self.roof_terrace_area_sqm + self.yard_area_sqm +
                  self.gallery_area_sqm)
        return total

    @property
    def customer_full_name(self):
        """Get customer full name"""
        if self.customer:
            return self.customer.full_name
        elif self.customer_first_name or self.customer_last_name:
            return f"{self.customer_first_name} {self.customer_last_name}".strip()
        return ""

    @property
    def is_sold(self):
        """Check if unit is sold"""
        return self.unit_status == 'SOLD'

    @property
    def is_available(self):
        """Check if unit is available for sale"""
        return self.unit_status == 'FOR_SALE'


# ============================================================================
# SALES TRANSACTION
# ============================================================================

class SalesTransaction(models.Model):
    """Individual apartment sale transactions"""

    SALE_STATUS = [
        ('AGREEMENT', 'הסכם / Agreement'),
        ('CONTRACT_SIGNED', 'חוזה נחתם / Contract Signed'),
        ('CANCELLED', 'בוטל / Cancelled'),
        ('COMPLETED', 'הושלם / Completed'),
    ]

    PAYMENT_TERMS = [
        ('CASH', 'מזומן / Cash'),
        ('MORTGAGE', 'משכנתא / Mortgage'),
        ('MIXED', 'שילוב / Mixed'),
        ('INSTALLMENTS', 'תשלומים / Installments'),
    ]

    SALE_TYPE = [
        ('REGULAR', 'רגיל / Regular Sale'),
        ('COMPENSATION', 'תמורה / Compensation'),
        ('RENTAL', 'השכרה / Rental'),
    ]

    # Links
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='sales_transactions',
        verbose_name="פרויקט / Project"
    )
    apartment = models.OneToOneField(
        ApartmentInventory,
        on_delete=models.CASCADE,
        related_name='sale_transaction',
        verbose_name="דירה / Apartment"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='purchases',
        verbose_name="לקוח / Customer"
    )

    # Sale Details
    sale_type = models.CharField(
        max_length=20,
        choices=SALE_TYPE,
        default='REGULAR',
        verbose_name="סוג מכירה / Sale Type"
    )
    agreement_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="תאריך הסכם / Agreement Date"
    )
    contract_date = models.DateField(
        verbose_name="תאריך חוזה / Contract Date"
    )
    delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="תאריך מסירה / Delivery Date"
    )
    sale_status = models.CharField(
        max_length=20,
        choices=SALE_STATUS,
        default='AGREEMENT',
        verbose_name="סטטוס / Status"
    )

    # Pricing
    original_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="מחיר מקורי / Original Price"
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="הנחה % / Discount Percent"
    )
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="הנחה סכום / Discount Amount"
    )
    final_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="מחיר סופי / Final Price"
    )

    # Payment Terms
    payment_terms = models.CharField(
        max_length=20,
        choices=PAYMENT_TERMS,
        default='MIXED',
        verbose_name="אופן תשלום / Payment Terms"
    )
    down_payment_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="מקדמה / Down Payment"
    )
    mortgage_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="משכנתא / Mortgage Amount"
    )

    # Additional Information
    notes = models.TextField(
        blank=True,
        verbose_name="הערות / Notes"
    )
    contract_file = models.FileField(
        upload_to='contracts/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="קובץ חוזה / Contract File"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales_created',
        verbose_name="נוצר על ידי / Created By"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_transactions'
        verbose_name = 'Sale Transaction'
        verbose_name_plural = 'Sales Transactions'
        ordering = ['-contract_date']

    def __str__(self):
        return f"{self.apartment.unit_unique_id} - {self.customer.full_name}"

    def save(self, *args, **kwargs):
        # Calculate final price if not set
        if not self.final_price:
            if self.discount_percent > 0:
                discount = self.original_price * (self.discount_percent / 100)
                self.discount_amount = discount
                self.final_price = self.original_price - discount
            elif self.discount_amount > 0:
                self.final_price = self.original_price - self.discount_amount
            else:
                self.final_price = self.original_price

        super().save(*args, **kwargs)

        # Update apartment status and link to customer
        if self.apartment:
            self.apartment.unit_status = 'SOLD'
            self.apartment.customer = self.customer
            self.apartment.customer_first_name = self.customer.first_name
            self.apartment.customer_last_name = self.customer.last_name
            self.apartment.contract_date = self.contract_date
            self.apartment.save()

    @property
    def total_paid(self):
        """Calculate total amount paid from payment schedule"""
        return sum(
            payment.actual_amount or 0
            for payment in self.payment_schedule.filter(payment_status='PAID')
        )

    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return self.final_price - self.total_paid


# Backward compatibility alias
class SalesLine(SalesTransaction):
    """Backward compatibility - use SalesTransaction instead"""
    class Meta:
        proxy = True


# ============================================================================
# CUSTOMER PAYMENT SCHEDULE
# ============================================================================

class CustomerPaymentSchedule(models.Model):
    """Payment schedule and tracking for apartment sales"""

    PAYMENT_TYPES = [
        ('DEPOSIT', 'מקדמה / Deposit'),
        ('MILESTONE', 'אבן דרך / Milestone'),
        ('MONTHLY', 'תשלום חודשי / Monthly'),
        ('INTERMEDIATE', 'תשלום ביניים / Intermediate Payment'),
        ('FINAL', 'תשלום סופי / Final Payment'),
        ('BANK_TRANSFER', 'העברה בנקאית / Bank Transfer'),
        ('MORTGAGE', 'משכנתא / Mortgage'),
        ('OTHER', 'אחר / Other'),
    ]

    PAYMENT_STATUS = [
        ('SCHEDULED', 'ממתין / Scheduled'),
        ('PAID', 'שולם / Paid'),
        ('PARTIAL', 'שולם חלקית / Partially Paid'),
        ('OVERDUE', 'באיחור / Overdue'),
        ('CANCELLED', 'בוטל / Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('CASH', 'מזומן / Cash'),
        ('CHECK', 'שיק / Check'),
        ('BANK_TRANSFER', 'העברה בנקאית / Bank Transfer'),
        ('CREDIT_CARD', 'כרטיס אשראי / Credit Card'),
        ('MORTGAGE', 'משכנתא / Mortgage'),
        ('OTHER', 'אחר / Other'),
    ]

    # Links
    sales_transaction = models.ForeignKey(
        SalesTransaction,
        on_delete=models.CASCADE,
        related_name='payment_schedule',
        verbose_name="עסקת מכירה / Sales Transaction"
    )

    # Payment Plan
    payment_number = models.IntegerField(
        verbose_name="מספר תשלום / Payment #"
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        verbose_name="סוג תשלום / Payment Type"
    )
    payment_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="תיאור / Description"
    )

    # Scheduled Payment
    scheduled_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="סכום מתוכנן / Scheduled Amount"
    )
    scheduled_date = models.DateField(
        verbose_name="תאריך מתוכנן / Scheduled Date"
    )

    # Actual Payment
    actual_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="סכום ששולם / Actual Amount Paid"
    )
    actual_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="תאריך תשלום / Actual Payment Date"
    )

    # Payment Details
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='SCHEDULED',
        verbose_name="סטטוס / Status"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        blank=True,
        verbose_name="אמצעי תשלום / Payment Method"
    )
    check_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="מספר שיק / Check Number"
    )
    bank_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="בנק / Bank Name"
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="אסמכתא / Reference Number"
    )

    # Delay Tracking
    days_delay = models.IntegerField(
        default=0,
        verbose_name="ימי איחור / Days Delay"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="הערות / Notes"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_payment_schedule'
        verbose_name = 'Payment Schedule'
        verbose_name_plural = 'Payment Schedules'
        ordering = ['scheduled_date', 'payment_number']

    def __str__(self):
        return f"{self.sales_transaction.customer.full_name} - תשלום #{self.payment_number}"

    def save(self, *args, **kwargs):
        # Auto-calculate delay on save
        self.calculate_delay()
        super().save(*args, **kwargs)

    def calculate_delay(self):
        """Calculate days delay if payment is overdue"""
        from datetime import date
        if self.payment_status not in ['PAID', 'CANCELLED'] and self.scheduled_date < date.today():
            self.days_delay = (date.today() - self.scheduled_date).days
            if self.days_delay > 0 and self.payment_status == 'SCHEDULED':
                self.payment_status = 'OVERDUE'
        else:
            self.days_delay = 0
        return self.days_delay

    def mark_as_paid(self, amount=None, payment_date=None, payment_method=None):
        """Mark payment as paid"""
        from datetime import date
        self.actual_amount = amount or self.scheduled_amount
        self.actual_date = payment_date or date.today()
        if payment_method:
            self.payment_method = payment_method

        if self.actual_amount >= self.scheduled_amount:
            self.payment_status = 'PAID'
        else:
            self.payment_status = 'PARTIAL'

        self.calculate_delay()
        self.save()

    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        from datetime import date
        return (self.payment_status not in ['PAID', 'CANCELLED'] and
                self.scheduled_date < date.today())

    @property
    def balance_due(self):
        """Calculate remaining balance for this payment"""
        if self.actual_amount:
            return self.scheduled_amount - self.actual_amount
        return self.scheduled_amount


# ============================================================================
# UNIT MIX
# ============================================================================

class UnitMix(models.Model):
    """Unit mix planning and summary"""
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='unit_mix'
    )
    
    apartment_type = models.CharField(max_length=100, verbose_name="Apartment Type")
    units_count = models.IntegerField(verbose_name="Units Count")
    
    # Average Areas
    avg_net_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Avg Net Area (sqm)"
    )
    avg_gross_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Avg Gross Area (sqm)"
    )
    avg_balcony_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Avg Balcony Area (sqm)"
    )
    avg_garden_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Avg Garden Area (sqm)"
    )
    
    # Flags
    is_penthouse = models.BooleanField(default=False)
    is_duplex = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'unitmix_lines'
        verbose_name = 'Unit Mix'
        verbose_name_plural = 'Unit Mix'
        ordering = ['apartment_type']
    
    def __str__(self):
        return f"{self.project} - {self.apartment_type} ({self.units_count} units)"


# ============================================================================
# SALES FORECAST
# ============================================================================

class SalesForecast(models.Model):
    """Revenue forecasting and sales projections"""
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='sales_forecasts'
    )
    
    forecast_date = models.DateField(verbose_name="Forecast Date")
    month_year = models.CharField(max_length=20, verbose_name="Month/Year")
    
    # Forecast
    expected_sales_count = models.IntegerField(
        default=0,
        verbose_name="Expected Sales Count"
    )
    expected_revenue_nis = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Expected Revenue (NIS)"
    )
    
    # Cumulative
    cumulative_sales_count = models.IntegerField(
        default=0,
        verbose_name="Cumulative Sales Count"
    )
    cumulative_revenue_nis = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Cumulative Revenue (NIS)"
    )
    
    notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales_forecasts_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_forecast'
        verbose_name = 'Sales Forecast'
        verbose_name_plural = 'Sales Forecasts'
        ordering = ['forecast_date']
        unique_together = [['project', 'month_year']]
    
    def __str__(self):
        return f"{self.project} - {self.month_year}"
