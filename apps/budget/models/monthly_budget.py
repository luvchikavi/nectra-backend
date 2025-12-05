from django.db import models
from django.utils import timezone
from apps.projects.models import Project

class MonthlyBudgetReport(models.Model):
    """
    Stores a pre-calculated snapshot of a project's financial status for a given month.
    This is the engine for the monthly monitoring report.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="budget_reports")
    month = models.IntegerField(help_text="The month of the report (1-12)")
    year = models.IntegerField(help_text="The year of the report")

    # Report number for sequential tracking (Report 1, Report 2, etc.)
    report_number = models.PositiveIntegerField(
        default=1,
        help_text="Sequential report number for this project"
    )

    # Report metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # ========================================================================
    # DATA FOR THE GRAPHS (Image 1)
    # Stores the final percentage values for the 5 key metrics.
    # ========================================================================

    # Metric 1: Total Budget Usage
    total_budget_usage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    prev_month_total_budget_usage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Metric 2: Direct Building Cost Usage
    direct_building_usage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    prev_month_direct_building_usage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Metric 3: Actual Construction Progress
    construction_progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    prev_month_construction_progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Metric 4: Signed Contracts
    signed_contracts_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    prev_month_signed_contracts_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Metric 5: "Qualified" Sales (Approved with >15% paid)
    qualified_sales_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    prev_month_qualified_sales_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)


    # ========================================================================
    # DATA FOR THE TABLE (Image 2)
    # A JSON field to hold the entire "Detailed Cost - up to date" table data.
    # ========================================================================
    
    detailed_cost_breakdown = models.JSONField(
        default=dict,
        help_text="Stores the full cost breakdown table for the month."
    )

    # ========================================================================
    # FINANCIAL SUMMARY FOR THE MONTH
    # High-level summary of income, costs, and balances.
    # ========================================================================
    expected_income_monthly = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    actual_income_monthly = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Progress-based earned cost for the month
    earned_cost_monthly = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    # Actual cash out from bank statements for the month
    actual_cash_out_monthly = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Budget Balance = Expected Income vs. Earned (Progress) Cost
    balance_monthly = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    # Cash Flow = Actual Income vs. Actual Cash Out
    cash_flow_monthly = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # ========================================================================
    # PHYSICAL VS FINANCIAL EXECUTION (Image 3)
    # Compares construction progress vs financial spending
    # ========================================================================

    # Physical execution (based on construction progress percentage)
    physical_execution_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    physical_execution_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Financial execution (based on approved payments/invoices)
    financial_execution_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    financial_execution_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Gap between physical and financial (Physical - Financial)
    physical_financial_gap_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    physical_financial_gap_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Pending checks/invoices awaiting approval
    checks_pending_approval = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Retention amount held back from contractors
    retention_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # ========================================================================
    # BANK TRANSACTION CATEGORIZATION
    # Tracks different types of bank transactions
    # ========================================================================
    bank_transactions_summary = models.JSONField(
        default=dict,
        help_text="Summary of bank transactions by category"
    )
    # Example JSON Structure:
    # {
    #   "purchase_receipts": 500000,
    #   "loans": 1000000,
    #   "surplus_release": 200000,
    #   "equity_deposit": 300000,
    #   "financing": 150000,
    #   "budget_performance": 50000,
    #   "total_in": 1500000,
    #   "total_out": 700000,
    #   "balance": 800000
    # }

    # Example JSON Structure:
    # {
    #   "land_expenses": {
    #     "prev_aggregate": 1000000,
    #     "monthly_outcome": 50000,
    #     "current_aggregate": 1050000,
    #     "estimated_balance": 150000,
    #     "total_estimated": 1200000,
    #     "percent_spent": 87.5
    #   },
    #   "general_costs": { ... },
    #   "establishment": { ... },
    #   "total":         { ... }
    # }

    class Meta:
        # Ensures we only have one report per project per month
        unique_together = ('project', 'year', 'month')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.project.project_name} - Report for {self.year}-{self.month:02d}"
