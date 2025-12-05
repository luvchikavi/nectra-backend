"""
Reports API Views
Provides modular report generation based on selected data modules
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.projects.models import Project, ProjectDataInputs


class AvailableModulesView(APIView):
    """
    Returns the list of available report modules organized by category.
    """
    def get(self, request, *args, **kwargs):
        modules = {
            "project_info": {
                "label": "פרטי פרויקט",
                "modules": [
                    {"id": "project_details", "name": "פרטים כלליים", "icon": "info"},
                    {"id": "project_dates", "name": "לוח זמנים", "icon": "calendar_today"},
                    {"id": "project_location", "name": "מיקום", "icon": "place"},
                ]
            },
            "sales": {
                "label": "מכירות והכנסות",
                "modules": [
                    {"id": "revenue_residential", "name": "הכנסות דירות", "icon": "apartment"},
                    {"id": "revenue_commercial", "name": "הכנסות מסחרי", "icon": "store"},
                    {"id": "revenue_parking", "name": "הכנסות חניות", "icon": "local_parking"},
                    {"id": "sales_summary", "name": "סיכום מכירות", "icon": "summarize"},
                ]
            },
            "financial": {
                "label": "פיננסי",
                "modules": [
                    {"id": "financing", "name": "מימון", "icon": "account_balance"},
                    {"id": "equity_deposits", "name": "הון עצמי", "icon": "savings"},
                    {"id": "bank_transactions", "name": "תנועות בנק", "icon": "receipt"},
                ]
            },
            "construction": {
                "label": "בנייה",
                "modules": [
                    {"id": "construction_progress", "name": "התקדמות בנייה", "icon": "construction"},
                    {"id": "cost_index", "name": "מדד תשומות", "icon": "trending_up"},
                ]
            },
            "budget": {
                "label": "תקציב",
                "modules": [
                    {"id": "budget_land", "name": "עלויות קרקע", "icon": "landscape"},
                    {"id": "budget_construction", "name": "עלויות בנייה", "icon": "build"},
                    {"id": "budget_soft_costs", "name": "עלויות רכות", "icon": "receipt_long"},
                    {"id": "budget_financing", "name": "עלויות מימון", "icon": "percent"},
                    {"id": "budget_marketing", "name": "שיווק ומכירות", "icon": "campaign"},
                    {"id": "budget_management", "name": "ניהול פרויקט", "icon": "manage_accounts"},
                    {"id": "budget_summary", "name": "סיכום תקציב", "icon": "summarize"},
                ]
            },
            "monthly": {
                "label": "דוחות תקופתיים",
                "modules": [
                    {"id": "monthly_cash_flow", "name": "תזרים חודשי", "icon": "show_chart"},
                    {"id": "monthly_progress", "name": "דוח חודשי", "icon": "assessment"},
                    {"id": "kpi_summary", "name": "מדדי ביצוע", "icon": "analytics"},
                ]
            }
        }
        return Response(modules)


class GenerateReportView(APIView):
    """
    Generate a report for a specific project with selected modules.
    POST /api/v1/reports/generate/
    Body: { project_id: int, modules: string[] }
    """

    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        modules = request.data.get('modules', [])

        if not project_id:
            return Response(
                {"error": "project_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not modules:
            return Response(
                {"error": "At least one module must be selected"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get project
        project = get_object_or_404(Project, pk=project_id)

        # Get project data inputs
        try:
            data_inputs = project.data_inputs
        except ProjectDataInputs.DoesNotExist:
            data_inputs = None

        # Build report data
        report_data = {
            "project": {
                "id": project.id,
                "name": project.project_name,
                "company": project.company_name,
            },
            "generated_at": str(timezone.now()),
            "modules": {}
        }

        # Fetch data for each requested module
        for module_id in modules:
            module_data = self._get_module_data(module_id, project, data_inputs)
            if module_data is not None:
                report_data["modules"][module_id] = module_data

        return Response(report_data)

    def _get_module_data(self, module_id, project, data_inputs):
        """
        Fetch data for a specific module from project data inputs.
        """
        if data_inputs is None:
            return None

        # Map module IDs to data input fields
        module_mapping = {
            # Project Info
            "project_details": lambda: {
                "project_name": project.project_name,
                "company_name": project.company_name,
                "city": project.city,
                "address": project.address,
                "developer": getattr(data_inputs, 'developer', None) or {},
            },
            "project_dates": lambda: getattr(data_inputs, 'dates', None) or {},
            "project_location": lambda: {
                "city": project.city,
                "address": project.address,
                "block": getattr(data_inputs, 'block', None),
                "parcel": getattr(data_inputs, 'parcel', None),
            },

            # Sales & Revenue
            "revenue_residential": lambda: getattr(data_inputs, 'revenue_residential', None) or [],
            "revenue_commercial": lambda: getattr(data_inputs, 'revenue_commercial', None) or [],
            "revenue_parking": lambda: getattr(data_inputs, 'revenue_parking', None) or [],
            "sales_summary": lambda: self._calculate_sales_summary(data_inputs),

            # Financial
            "financing": lambda: getattr(data_inputs, 'financing', None) or {},
            "equity_deposits": lambda: self._get_equity_deposits(project),
            "bank_transactions": lambda: self._get_bank_transactions(project),

            # Construction
            "construction_progress": lambda: self._get_construction_progress(project),
            "cost_index": lambda: getattr(data_inputs, 'cost_index', None) or {},

            # Budget
            "budget_land": lambda: getattr(data_inputs, 'budget_land', None) or [],
            "budget_construction": lambda: getattr(data_inputs, 'budget_construction', None) or [],
            "budget_soft_costs": lambda: getattr(data_inputs, 'budget_soft_costs', None) or [],
            "budget_financing": lambda: getattr(data_inputs, 'budget_financing', None) or [],
            "budget_marketing": lambda: getattr(data_inputs, 'budget_marketing', None) or [],
            "budget_management": lambda: getattr(data_inputs, 'budget_management', None) or [],
            "budget_summary": lambda: self._calculate_budget_summary(data_inputs),

            # Monthly Reports
            "monthly_cash_flow": lambda: getattr(data_inputs, 'cash_flow', None) or [],
            "monthly_progress": lambda: getattr(data_inputs, 'monthly_progress', None) or {},
            "kpi_summary": lambda: self._calculate_kpi_summary(project, data_inputs),
        }

        if module_id in module_mapping:
            try:
                return module_mapping[module_id]()
            except Exception as e:
                return {"error": str(e)}

        return None

    def _calculate_sales_summary(self, data_inputs):
        """Calculate summary from revenue data."""
        summary = {
            "total_residential": 0,
            "total_commercial": 0,
            "total_parking": 0,
            "grand_total": 0,
            "unit_counts": {
                "residential": 0,
                "commercial": 0,
                "parking": 0,
            }
        }

        # Residential
        residential = getattr(data_inputs, 'revenue_residential', None) or []
        for item in residential:
            if isinstance(item, dict):
                value = item.get('total_value_with_vat', 0) or item.get('שווי כולל מע"מ', 0)
                summary["total_residential"] += float(value or 0)
                summary["unit_counts"]["residential"] += 1

        # Commercial
        commercial = getattr(data_inputs, 'revenue_commercial', None) or []
        for item in commercial:
            if isinstance(item, dict):
                value = item.get('total_value_with_vat', 0) or item.get('שווי כולל מע"מ', 0)
                summary["total_commercial"] += float(value or 0)
                summary["unit_counts"]["commercial"] += 1

        # Parking
        parking = getattr(data_inputs, 'revenue_parking', None) or []
        for item in parking:
            if isinstance(item, dict):
                value = item.get('total_value_with_vat', 0) or item.get('שווי כולל מע"מ', 0)
                summary["total_parking"] += float(value or 0)
                summary["unit_counts"]["parking"] += 1

        summary["grand_total"] = (
            summary["total_residential"] +
            summary["total_commercial"] +
            summary["total_parking"]
        )

        return summary

    def _calculate_budget_summary(self, data_inputs):
        """Calculate budget summary from all budget sections."""
        categories = [
            'budget_land',
            'budget_construction',
            'budget_soft_costs',
            'budget_financing',
            'budget_marketing',
            'budget_management',
        ]

        summary = {
            "by_category": {},
            "grand_total": 0
        }

        for category in categories:
            items = getattr(data_inputs, category, None) or []
            category_total = 0
            for item in items:
                if isinstance(item, dict):
                    amount = item.get('amount', 0) or item.get('סכום', 0)
                    category_total += float(amount or 0)
            summary["by_category"][category] = category_total
            summary["grand_total"] += category_total

        return summary

    def _get_equity_deposits(self, project):
        """Get equity deposits for the project."""
        from apps.projects.models import EquityDeposit
        deposits = EquityDeposit.objects.filter(project=project)
        return [
            {
                "id": d.id,
                "deposit_date": str(d.deposit_date) if d.deposit_date else None,
                "amount": float(d.amount),
                "source": d.source,
                "description": d.description,
            }
            for d in deposits
        ]

    def _get_bank_transactions(self, project):
        """Get recent bank transactions for the project."""
        from apps.projects.models import BankTransaction
        transactions = BankTransaction.objects.filter(project=project).order_by('-transaction_date')[:50]
        return [
            {
                "id": t.id,
                "transaction_date": str(t.transaction_date) if t.transaction_date else None,
                "amount": float(t.amount),
                "description": t.description,
                "category": t.category,
                "status": t.status,
            }
            for t in transactions
        ]

    def _get_construction_progress(self, project):
        """Get construction progress data."""
        from apps.projects.models import ConstructionProgress
        progress = ConstructionProgress.objects.filter(project=project).order_by('-recorded_at')[:12]
        return [
            {
                "id": p.id,
                "stage": p.stage,
                "progress_percent": float(p.progress_percent) if p.progress_percent else 0,
                "recorded_at": str(p.recorded_at) if p.recorded_at else None,
                "notes": p.notes,
            }
            for p in progress
        ]

    def _calculate_kpi_summary(self, project, data_inputs):
        """Calculate key performance indicators."""
        from apps.sales.models import SalesTransaction, ApartmentInventory

        kpis = {
            "sales_progress": 0,
            "construction_progress": 0,
            "budget_used_percent": 0,
            "equity_collected_percent": 0,
        }

        # Sales progress
        try:
            total_units = ApartmentInventory.objects.filter(project=project).count()
            sold_units = ApartmentInventory.objects.filter(project=project, unit_status='SOLD').count()
            if total_units > 0:
                kpis["sales_progress"] = (sold_units / total_units) * 100
        except Exception:
            pass

        # Construction progress from latest record
        try:
            from apps.projects.models import ConstructionProgress
            latest = ConstructionProgress.objects.filter(project=project).order_by('-recorded_at').first()
            if latest:
                kpis["construction_progress"] = float(latest.progress_percent or 0)
        except Exception:
            pass

        # Equity collected
        try:
            financing = getattr(data_inputs, 'financing', None) or {}
            required = float(financing.get('bank_required_equity', 0) or 0)
            if required > 0:
                from apps.projects.models import EquityDeposit
                deposited = EquityDeposit.objects.filter(project=project).aggregate(
                    total=Sum('amount')
                )['total'] or 0
                kpis["equity_collected_percent"] = (float(deposited) / required) * 100
        except Exception:
            pass

        return kpis


# Import timezone for the generate view
from django.utils import timezone
from django.db.models import Sum
