# in backend/apps/budget/services.py

from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from apps.projects.models import Project, ConstructionProgress, ConstructionProgressSnapshot, BankTransaction
from apps.sales.models import SalesTransaction, CustomerPaymentSchedule
from .models import MonthlyBudgetReport


def convert_decimals_to_float(obj):
    """Recursively convert Decimal values to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_float(item) for item in obj]
    return obj

class MonthlyReportGenerator:
    """
    A service class responsible for generating the comprehensive MonthlyBudgetReport
    by gathering and calculating data from various apps.
    """

    def __init__(self, project: Project, year: int, month: int):
        self.project = project
        self.year = year
        self.month = month
        self.start_date = date(year, month, 1)
        self.end_date = (self.start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        self.prev_report = self._get_previous_report()

    def _get_previous_report(self):
        """Fetches the report from the previous month to get historical data."""
        prev_month_date = self.start_date - timedelta(days=1)
        try:
            return MonthlyBudgetReport.objects.get(
                project=self.project,
                year=prev_month_date.year,
                month=prev_month_date.month
            )
        except MonthlyBudgetReport.DoesNotExist:
            return None

    def generate_report(self) -> MonthlyBudgetReport:
        """
        Main method to orchestrate the report generation.
        It calls various helper methods to calculate metrics and saves the report.
        """
        income_data = self._calculate_income_data()
        cost_data = self._calculate_cost_data()
        progress_data = self._calculate_progress_data()
        sales_data = self._calculate_sales_data()
        cash_flow_data = self._calculate_actual_cash_flow()
        execution_data = self._calculate_physical_financial_execution()
        bank_summary = self._calculate_bank_transactions_summary()

        # Combine all calculated data
        all_data = {
            **income_data,
            **cost_data,
            **progress_data,
            **sales_data,
            **cash_flow_data,
            **execution_data,
            **bank_summary,
        }

        # Calculate final summary fields - ensure consistent types (use Decimal for calculations)
        earned_cost_monthly = Decimal(str(all_data.get('detailed_cost_breakdown', {}).get('total', {}).get('monthly_outcome', 0)))
        expected_income = Decimal(str(all_data.get('expected_income_monthly', 0)))
        actual_income = Decimal(str(all_data.get('actual_income_monthly', 0)))
        actual_cash_out = Decimal(str(all_data.get('actual_cash_out_monthly', 0)))

        all_data['earned_cost_monthly'] = earned_cost_monthly
        all_data['balance_monthly'] = expected_income - earned_cost_monthly
        all_data['cash_flow_monthly'] = actual_income - actual_cash_out

        # Calculate sequential report number for this project
        all_data['report_number'] = self._get_next_report_number()

        report, created = MonthlyBudgetReport.objects.update_or_create(
            project=self.project,
            year=self.year,
            month=self.month,
            defaults=all_data
        )
        return report

    def _get_next_report_number(self):
        """
        Calculate the next sequential report number for this project.
        If updating an existing report, use its number. Otherwise, increment.
        """
        # Check if a report for this month already exists
        existing = MonthlyBudgetReport.objects.filter(
            project=self.project,
            year=self.year,
            month=self.month
        ).first()

        if existing:
            return existing.report_number

        # Get the highest report number for this project and increment
        last_report = MonthlyBudgetReport.objects.filter(
            project=self.project
        ).order_by('-report_number').first()

        return (last_report.report_number + 1) if last_report else 1

    def _calculate_actual_cash_flow(self):
        """Calculates actual cash out for the month from bank transactions."""
        actual_cash_out = BankTransaction.objects.filter(
            project=self.project,
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date,
            transaction_type='DEBIT'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        return {
            'actual_cash_out_monthly': actual_cash_out,
        }


    def _calculate_income_data(self):
        """
        Calculates expected and actual income for the month from payment schedules.
        """
        expected_income = CustomerPaymentSchedule.objects.filter(
            sales_transaction__project=self.project,
            scheduled_date__gte=self.start_date,
            scheduled_date__lte=self.end_date
        ).aggregate(total=models.Sum('scheduled_amount'))['total'] or Decimal('0')

        actual_income = CustomerPaymentSchedule.objects.filter(
            sales_transaction__project=self.project,
            actual_date__gte=self.start_date,
            actual_date__lte=self.end_date,
            payment_status='PAID'
        ).aggregate(total=models.Sum('actual_amount'))['total'] or Decimal('0')

        return {
            'expected_income_monthly': expected_income,
            'actual_income_monthly': actual_income,
        }

    def _calculate_cost_data(self):
        """
        Calculates all cost-related data for the monthly report.
        - Calculates progress-based "earned cost" for the month.
        - Builds the detailed cost breakdown table.
        - Calculates total and direct building budget usage percentages.
        """
        try:
            progress = ConstructionProgress.objects.get(project=self.project)
            tasks = progress.tasks or []
        except ConstructionProgress.DoesNotExist:
            tasks = []

        # Get the previous month's progress snapshot to calculate deltas
        prev_month_date = self.start_date - timedelta(days=1)
        try:
            prev_snapshot = ConstructionProgressSnapshot.objects.get(
                project=self.project,
                year=prev_month_date.year,
                month=prev_month_date.month
            )
            prev_tasks = {task['task_number']: task for task in prev_snapshot.tasks_snapshot}
        except ConstructionProgressSnapshot.DoesNotExist:
            prev_tasks = {}

        # Define how chapters from the progress table map to our report categories
        # This is a key business logic decision.
        # For now, we'll use a simple mapping. This can be expanded.
        CATEGORY_MAPPING = {
            'קרקע': 'land_expenses',
            'כללי': 'general_costs',
            'שלד': 'establishment',
            'גמרים': 'establishment',
            # Add other chapter mappings here...
        }
        DEFAULT_CATEGORY = 'general_costs'

        # Initialize the structure for the detailed breakdown
        breakdown = {
            cat: {'prev_aggregate': 0, 'monthly_outcome': 0, 'current_aggregate': 0, 'estimated_balance': 0, 'total_estimated': 0, 'percent_spent': 0}
            for cat in ['land_expenses', 'general_costs', 'establishment', 'total']
        }
        
        total_planned_budget = Decimal('0')
        direct_building_planned_budget = Decimal('0')

        for task in tasks:
            task_num = task.get('task_number')
            budgeted_amount = Decimal(task.get('budgeted_amount', 0))
            current_completion = Decimal(task.get('total_completion', 0))
            chapter = task.get('chapter', '')

            total_planned_budget += budgeted_amount
            # Define what counts as "direct building" cost
            if chapter in ['שלד', 'גמרים']:
                direct_building_planned_budget += budgeted_amount

            # Get previous completion to calculate delta
            prev_completion = Decimal(prev_tasks.get(task_num, {}).get('total_completion', 0))
            progress_delta = current_completion - prev_completion

            monthly_cost = budgeted_amount * progress_delta
            current_aggregate_cost = budgeted_amount * current_completion
            prev_aggregate_cost = budgeted_amount * prev_completion

            category = CATEGORY_MAPPING.get(chapter, DEFAULT_CATEGORY)

            breakdown[category]['monthly_outcome'] += monthly_cost
            breakdown[category]['current_aggregate'] += current_aggregate_cost
            breakdown[category]['prev_aggregate'] += prev_aggregate_cost
            breakdown[category]['total_estimated'] += budgeted_amount

        # Calculate totals and balances
        for category, values in breakdown.items():
            if category == 'total': continue
            values['estimated_balance'] = values['total_estimated'] - values['current_aggregate']
            if values['total_estimated'] > 0:
                values['percent_spent'] = (values['current_aggregate'] / values['total_estimated']) * 100
            
            # Sum up to the 'total' category
            for key in values:
                breakdown['total'][key] += values[key]

        # Final calculation for the 'total' row's percentage
        if breakdown['total']['total_estimated'] > 0:
            breakdown['total']['percent_spent'] = (breakdown['total']['current_aggregate'] / breakdown['total']['total_estimated']) * 100

        # Calculate overall budget usage percentages
        total_budget_usage_percent = (breakdown['total']['current_aggregate'] / total_planned_budget) * 100 if total_planned_budget > 0 else 0
        
        # Calculate direct building usage
        direct_building_current_aggregate = breakdown['establishment']['current_aggregate'] # Assuming 'establishment' covers direct building
        direct_building_usage_percent = (direct_building_current_aggregate / direct_building_planned_budget) * 100 if direct_building_planned_budget > 0 else 0

        # Get previous month's data from the last report
        prev_month_total_budget_usage_percent = self.prev_report.total_budget_usage_percent if self.prev_report else 0
        prev_month_direct_building_usage_percent = self.prev_report.direct_building_usage_percent if self.prev_report else 0

        # Convert Decimals to floats for JSON serialization
        breakdown = convert_decimals_to_float(breakdown)

        return {
            'detailed_cost_breakdown': breakdown,
            'total_budget_usage_percent': float(total_budget_usage_percent) if isinstance(total_budget_usage_percent, Decimal) else total_budget_usage_percent,
            'prev_month_total_budget_usage_percent': prev_month_total_budget_usage_percent,
            'direct_building_usage_percent': float(direct_building_usage_percent) if isinstance(direct_building_usage_percent, Decimal) else direct_building_usage_percent,
            'prev_month_direct_building_usage_percent': prev_month_direct_building_usage_percent,
        }

    def _calculate_progress_data(self):
        """
        Calculates the construction progress percentage.
        """
        try:
            progress = ConstructionProgress.objects.get(project=self.project)
            current_progress = progress.overall_completion_percentage
        except ConstructionProgress.DoesNotExist:
            current_progress = 0

        prev_month_progress = self.prev_report.construction_progress_percent if self.prev_report else 0

        return {
            'construction_progress_percent': current_progress,
            'prev_month_construction_progress_percent': prev_month_progress,
        }

    def _calculate_sales_data(self):
        """
        Calculates sales data metrics:
        1. Percentage of units with signed contracts.
        2. Percentage of "qualified" sales (contract signed and >15% paid).
        """
        total_units = self.project.apartments.count()
        if total_units == 0:
            return {
                'signed_contracts_percent': 0,
                'prev_month_signed_contracts_percent': 0,
                'qualified_sales_percent': 0,
                'prev_month_qualified_sales_percent': 0,
            }

        # 1. Calculate Signed Contracts Percentage
        sold_units = self.project.apartments.filter(unit_status='SOLD').count()
        signed_contracts_percent = (sold_units / total_units) * 100

        # 2. Calculate "Qualified" Sales Percentage
        qualified_sales_count = 0
        sales_transactions = SalesTransaction.objects.filter(project=self.project).prefetch_related('payment_schedule')
        
        for sale in sales_transactions:
            if sale.final_price and sale.final_price > 0:
                total_paid = sum(p.actual_amount for p in sale.payment_schedule.filter(payment_status='PAID') if p.actual_amount)
                paid_percent = (total_paid / sale.final_price) * 100
                if paid_percent > 15:
                    qualified_sales_count += 1
        
        qualified_sales_percent = (qualified_sales_count / total_units) * 100

        # 3. Get Previous Month's Data
        prev_month_signed_contracts_percent = self.prev_report.signed_contracts_percent if self.prev_report else 0
        prev_month_qualified_sales_percent = self.prev_report.qualified_sales_percent if self.prev_report else 0

        return {
            'signed_contracts_percent': signed_contracts_percent,
            'prev_month_signed_contracts_percent': prev_month_signed_contracts_percent,
            'qualified_sales_percent': qualified_sales_percent,
            'prev_month_qualified_sales_percent': prev_month_qualified_sales_percent,
        }

    def _calculate_physical_financial_execution(self):
        """
        Calculates physical vs financial execution comparison.
        - Physical execution: Based on actual construction progress
        - Financial execution: Based on approved payments/invoices to contractors
        """
        # Get total project budget
        try:
            progress = ConstructionProgress.objects.get(project=self.project)
            tasks = progress.tasks or []
        except ConstructionProgress.DoesNotExist:
            tasks = []

        total_budget = Decimal('0')
        physical_value = Decimal('0')

        for task in tasks:
            budgeted_amount = Decimal(task.get('budgeted_amount', 0))
            completion = Decimal(task.get('total_completion', 0))
            total_budget += budgeted_amount
            physical_value += budgeted_amount * completion

        # Physical execution percentage
        physical_execution_percent = (physical_value / total_budget * 100) if total_budget > 0 else Decimal('0')

        # Financial execution: Sum of all approved debit transactions (payments made)
        financial_value = BankTransaction.objects.filter(
            project=self.project,
            transaction_date__lte=self.end_date,
            transaction_type='DEBIT',
            status='APPROVED'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        financial_execution_percent = (financial_value / total_budget * 100) if total_budget > 0 else Decimal('0')

        # Gap = Physical - Financial (positive means ahead in work vs payments)
        gap_percent = physical_execution_percent - financial_execution_percent
        gap_value = physical_value - financial_value

        # Pending checks: PENDING debit transactions
        checks_pending = BankTransaction.objects.filter(
            project=self.project,
            transaction_type='DEBIT',
            status='PENDING'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        # Retention: This would typically come from contractor payment records
        # For now, calculate as a percentage of payments (e.g., 5% retention)
        retention_percent = Decimal('0.05')
        retention_amount = financial_value * retention_percent

        return {
            'physical_execution_percent': physical_execution_percent,
            'physical_execution_value': physical_value,
            'financial_execution_percent': financial_execution_percent,
            'financial_execution_value': financial_value,
            'physical_financial_gap_percent': gap_percent,
            'physical_financial_gap_value': gap_value,
            'checks_pending_approval': checks_pending,
            'retention_amount': retention_amount,
        }

    def _calculate_bank_transactions_summary(self):
        """
        Calculates summary of bank transactions by category for the month.
        Categories: Purchase receipts, Loans, Surplus release, Equity deposit, Financing, Budget/Performance
        """
        # Define the category mapping based on BankTransaction.TRANSACTION_CATEGORY choices
        CATEGORY_FIELDS = {
            'PURCHASE_RECEIPTS': 'purchase_receipts',
            'LOANS': 'loans',
            'SURPLUS_RELEASE': 'surplus_release',
            'EQUITY_DEPOSIT': 'equity_deposit',
            'FINANCING': 'financing',
            'BUDGET_PERFORMANCE': 'budget_performance',
        }

        summary = {
            'purchase_receipts': Decimal('0'),
            'loans': Decimal('0'),
            'surplus_release': Decimal('0'),
            'equity_deposit': Decimal('0'),
            'financing': Decimal('0'),
            'budget_performance': Decimal('0'),
            'total_in': Decimal('0'),
            'total_out': Decimal('0'),
            'balance': Decimal('0'),
        }

        # Get all transactions for the month
        transactions = BankTransaction.objects.filter(
            project=self.project,
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date,
            status='APPROVED'
        )

        for txn in transactions:
            amount = txn.amount or Decimal('0')
            category = txn.category if hasattr(txn, 'category') else None

            # Map to summary category
            if category and category in CATEGORY_FIELDS:
                summary[CATEGORY_FIELDS[category]] += amount

            # Track totals by transaction type
            if txn.transaction_type == 'CREDIT':
                summary['total_in'] += amount
            elif txn.transaction_type == 'DEBIT':
                summary['total_out'] += amount

        summary['balance'] = summary['total_in'] - summary['total_out']

        # Convert Decimals to float for JSON serialization
        summary = {k: float(v) for k, v in summary.items()}

        return {
            'bank_transactions_summary': summary,
        }

