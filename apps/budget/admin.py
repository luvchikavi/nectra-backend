from django.contrib import admin
from .models import *


# Direct Build
@admin.register(DirectBuildLine)
class DirectBuildLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'quantity', 'unit_price', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(DirectBuildSummary)
class DirectBuildSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Land Cost (EQUITY ELIGIBLE)
@admin.register(LandCostLine)
class LandCostLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'is_equity_eligible', 'total_amount']
    list_filter = ['project', 'is_equity_eligible']
    search_fields = ['description', 'land_type']

@admin.register(LandCostSummary)
class LandCostSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Suppliers (EQUITY ELIGIBLE)
@admin.register(SuppliersLine)
class SuppliersLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'supplier_name', 'service_type', 'is_equity_eligible', 'total_amount']
    list_filter = ['project', 'is_equity_eligible', 'service_type']
    search_fields = ['supplier_name', 'description']

@admin.register(SuppliersSummary)
class SuppliersSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Development Levies (EQUITY ELIGIBLE)
@admin.register(DevLeviesLine)
class DevLeviesLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'levy_type', 'authority', 'is_equity_eligible', 'total_amount']
    list_filter = ['project', 'is_equity_eligible', 'levy_type']
    search_fields = ['description', 'levy_type', 'authority']

@admin.register(DevLeviesSummary)
class DevLeviesSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Purchase Tax A (EQUITY ELIGIBLE)
@admin.register(PurchaseTaxALine)
class PurchaseTaxALineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'is_equity_eligible', 'total_amount']
    list_filter = ['project', 'is_equity_eligible']
    search_fields = ['description', 'tax_type']

@admin.register(PurchaseTaxASummary)
class PurchaseTaxASummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Purchase Tax B (EQUITY ELIGIBLE)
@admin.register(PurchaseTaxBLine)
class PurchaseTaxBLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'is_equity_eligible', 'total_amount']
    list_filter = ['project', 'is_equity_eligible']
    search_fields = ['description', 'tax_type']

@admin.register(PurchaseTaxBSummary)
class PurchaseTaxBSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# VAT
@admin.register(VATCSLine)
class VATCSLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(VATCSSummary)
class VATCSSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Management
@admin.register(ManagementLine)
class ManagementLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(ManagementSummary)
class ManagementSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Overhead
@admin.register(OverheadLine)
class OverheadLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(OverheadSummary)
class OverheadSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Maintenance
@admin.register(MaintenanceLine)
class MaintenanceLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(MaintenanceSummary)
class MaintenanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Rent
@admin.register(RentLine)
class RentLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(RentSummary)
class RentSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Electricity
@admin.register(ElectricityLine)
class ElectricityLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(ElectricitySummary)
class ElectricitySummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Site Insurance
@admin.register(SiteInsLine)
class SiteInsLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(SiteInsSummary)
class SiteInsSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Unexpected
@admin.register(UnexpectedLine)
class UnexpectedLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(UnexpectedSummary)
class UnexpectedSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Tenant Compensation
@admin.register(TenantsCompLine)
class TenantsCompLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(TenantsCompSummary)
class TenantsCompSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Upgrades
@admin.register(UpgradesLine)
class UpgradesLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(UpgradesSummary)
class UpgradesSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']


# Other Expenses
@admin.register(OtherExpLine)
class OtherExpLineAdmin(admin.ModelAdmin):
    list_display = ['project', 'line_number', 'description', 'total_amount']
    list_filter = ['project']
    search_fields = ['description']

@admin.register(OtherExpSummary)
class OtherExpSummaryAdmin(admin.ModelAdmin):
    list_display = ['project', 'total_lines', 'total_with_vat']
    list_filter = ['project']
