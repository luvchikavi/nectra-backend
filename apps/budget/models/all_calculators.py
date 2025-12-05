"""
All Budget Calculator Models
Auto-generated base structure for 17 calculators
Each has Lines and Summary tables
"""
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


# ============================================================================
# BASE CALCULATOR MODELS
# ============================================================================

class BaseCalculatorLine(models.Model):
    """Abstract base for all calculator line items"""
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='%(class)s_lines'
    )
    line_number = models.IntegerField(verbose_name="Line Number")
    description = models.CharField(max_length=500, verbose_name="Description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Monthly breakdown (36 months)
    month_1 = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    month_2 = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    month_3 = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    month_4 = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    month_5 = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    month_6 = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['line_number']
    
    def save(self, *args, **kwargs):
        # Auto-calculate total
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class BaseCalculatorSummary(models.Model):
    """Abstract base for all calculator summaries"""
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='%(class)s_summary'
    )
    total_lines = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_with_vat = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=3, default=0.17)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def calculate_totals(self):
        """Calculate summary from lines - override in subclasses"""
        pass


# ============================================================================
# 1. DIRECT BUILD (NOT equity eligible)
# ============================================================================

class DirectBuildLine(BaseCalculatorLine):
    """Direct construction costs - line items"""
    work_type = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'directbuild_lines'
        verbose_name = 'Direct Build Line'
        verbose_name_plural = 'Direct Build Lines'


class DirectBuildSummary(BaseCalculatorSummary):
    """Direct construction costs - summary"""
    
    class Meta:
        db_table = 'directbuild_summary'
        verbose_name = 'Direct Build Summary'
        verbose_name_plural = 'Direct Build Summaries'


# ============================================================================
# 2. LAND COST (100% equity eligible)
# ============================================================================

class LandCostLine(BaseCalculatorLine):
    """Land acquisition costs - line items"""
    land_type = models.CharField(max_length=200, blank=True)
    is_equity_eligible = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'landcost_lines'
        verbose_name = 'Land Cost Line'
        verbose_name_plural = 'Land Cost Lines'


class LandCostSummary(BaseCalculatorSummary):
    """Land acquisition costs - summary"""
    
    class Meta:
        db_table = 'landcost_summary'
        verbose_name = 'Land Cost Summary'
        verbose_name_plural = 'Land Cost Summaries'


# ============================================================================
# 3. SUPPLIERS (100% equity eligible)
# ============================================================================

class SuppliersLine(BaseCalculatorLine):
    """Consultant and supplier fees - line items"""
    supplier_name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=200)
    is_equity_eligible = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'suppliers_lines'
        verbose_name = 'Suppliers Line'
        verbose_name_plural = 'Suppliers Lines'


class SuppliersSummary(BaseCalculatorSummary):
    """Consultant and supplier fees - summary"""
    
    class Meta:
        db_table = 'suppliers_summary'
        verbose_name = 'Suppliers Summary'
        verbose_name_plural = 'Suppliers Summaries'


# ============================================================================
# 4. DEVELOPMENT LEVIES (equity eligible)
# ============================================================================

class DevLeviesLine(BaseCalculatorLine):
    """Development levies - line items"""
    levy_type = models.CharField(max_length=200)
    authority = models.CharField(max_length=200, blank=True)
    is_equity_eligible = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'devlevies_lines'
        verbose_name = 'Development Levy Line'
        verbose_name_plural = 'Development Levy Lines'


class DevLeviesSummary(BaseCalculatorSummary):
    """Development levies - summary"""
    
    class Meta:
        db_table = 'devlevies_summary'
        verbose_name = 'Development Levy Summary'
        verbose_name_plural = 'Development Levy Summaries'


# ============================================================================
# 5. PURCHASE TAX A (equity eligible)
# ============================================================================

class PurchaseTaxALine(BaseCalculatorLine):
    """Purchase tax A - line items"""
    tax_type = models.CharField(max_length=200, blank=True)
    is_equity_eligible = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'purchasetaxa_lines'
        verbose_name = 'Purchase Tax A Line'
        verbose_name_plural = 'Purchase Tax A Lines'


class PurchaseTaxASummary(BaseCalculatorSummary):
    """Purchase tax A - summary"""
    
    class Meta:
        db_table = 'purchasetaxa_summary'
        verbose_name = 'Purchase Tax A Summary'
        verbose_name_plural = 'Purchase Tax A Summaries'


# ============================================================================
# 6. PURCHASE TAX B (equity eligible)
# ============================================================================

class PurchaseTaxBLine(BaseCalculatorLine):
    """Purchase tax B - line items"""
    tax_type = models.CharField(max_length=200, blank=True)
    is_equity_eligible = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'purchasetaxb_lines'
        verbose_name = 'Purchase Tax B Line'
        verbose_name_plural = 'Purchase Tax B Lines'


class PurchaseTaxBSummary(BaseCalculatorSummary):
    """Purchase tax B - summary"""
    
    class Meta:
        db_table = 'purchasetaxb_summary'
        verbose_name = 'Purchase Tax B Summary'
        verbose_name_plural = 'Purchase Tax B Summaries'


# ============================================================================
# 7-17: REMAINING CALCULATORS (NOT equity eligible)
# ============================================================================

# VAT_CS
class VATCSLine(BaseCalculatorLine):
    class Meta:
        db_table = 'vat_cs_lines'
        verbose_name = 'VAT Line'
        verbose_name_plural = 'VAT Lines'

class VATCSSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'vat_cs_summary'
        verbose_name = 'VAT Summary'
        verbose_name_plural = 'VAT Summaries'


# Management
class ManagementLine(BaseCalculatorLine):
    class Meta:
        db_table = 'management_lines'
        verbose_name = 'Management Line'
        verbose_name_plural = 'Management Lines'

class ManagementSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'management_summary'
        verbose_name = 'Management Summary'
        verbose_name_plural = 'Management Summaries'


# Overhead
class OverheadLine(BaseCalculatorLine):
    class Meta:
        db_table = 'overhead_lines'
        verbose_name = 'Overhead Line'
        verbose_name_plural = 'Overhead Lines'

class OverheadSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'overhead_summary'
        verbose_name = 'Overhead Summary'
        verbose_name_plural = 'Overhead Summaries'


# Maintenance
class MaintenanceLine(BaseCalculatorLine):
    class Meta:
        db_table = 'maintenance_lines'
        verbose_name = 'Maintenance Line'
        verbose_name_plural = 'Maintenance Lines'

class MaintenanceSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'maintenance_summary'
        verbose_name = 'Maintenance Summary'
        verbose_name_plural = 'Maintenance Summaries'


# Rent
class RentLine(BaseCalculatorLine):
    class Meta:
        db_table = 'rent_lines'
        verbose_name = 'Rent Line'
        verbose_name_plural = 'Rent Lines'

class RentSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'rent_summary'
        verbose_name = 'Rent Summary'
        verbose_name_plural = 'Rent Summaries'


# Electricity
class ElectricityLine(BaseCalculatorLine):
    class Meta:
        db_table = 'electricity_lines'
        verbose_name = 'Electricity Line'
        verbose_name_plural = 'Electricity Lines'

class ElectricitySummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'electricity_summary'
        verbose_name = 'Electricity Summary'
        verbose_name_plural = 'Electricity Summaries'


# Site Insurance
class SiteInsLine(BaseCalculatorLine):
    class Meta:
        db_table = 'siteins_lines'
        verbose_name = 'Site Insurance Line'
        verbose_name_plural = 'Site Insurance Lines'

class SiteInsSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'siteins_summary'
        verbose_name = 'Site Insurance Summary'
        verbose_name_plural = 'Site Insurance Summaries'


# Unexpected
class UnexpectedLine(BaseCalculatorLine):
    class Meta:
        db_table = 'unexpected_lines'
        verbose_name = 'Unexpected Cost Line'
        verbose_name_plural = 'Unexpected Cost Lines'

class UnexpectedSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'unexpected_summary'
        verbose_name = 'Unexpected Cost Summary'
        verbose_name_plural = 'Unexpected Cost Summaries'


# Tenant Compensation
class TenantsCompLine(BaseCalculatorLine):
    class Meta:
        db_table = 'tenantscomp_lines'
        verbose_name = 'Tenant Compensation Line'
        verbose_name_plural = 'Tenant Compensation Lines'

class TenantsCompSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'tenantscomp_summary'
        verbose_name = 'Tenant Compensation Summary'
        verbose_name_plural = 'Tenant Compensation Summaries'


# Upgrades
class UpgradesLine(BaseCalculatorLine):
    class Meta:
        db_table = 'upgrades_lines'
        verbose_name = 'Upgrade Line'
        verbose_name_plural = 'Upgrade Lines'

class UpgradesSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'upgrades_summary'
        verbose_name = 'Upgrade Summary'
        verbose_name_plural = 'Upgrade Summaries'


# Other Expenses
class OtherExpLine(BaseCalculatorLine):
    class Meta:
        db_table = 'otherexp_lines'
        verbose_name = 'Other Expense Line'
        verbose_name_plural = 'Other Expense Lines'

class OtherExpSummary(BaseCalculatorSummary):
    class Meta:
        db_table = 'otherexp_summary'
        verbose_name = 'Other Expense Summary'
        verbose_name_plural = 'Other Expense Summaries'
