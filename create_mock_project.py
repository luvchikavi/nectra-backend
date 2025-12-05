#!/usr/bin/env python
"""
Script to create a comprehensive mock project with all test data
This includes: property details, developer info, financing, revenue forecast,
cost forecast, apartments, construction progress, bank transactions, and equity deposits.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.projects.models import (
    Project, ProjectDataInputs, BankTransaction,
    ConstructionProgress, EquityDeposit
)


def create_mock_project():
    """Create a comprehensive mock project with all data"""

    print("Creating Mock Project...")

    # Delete existing mock project if exists
    Project.objects.filter(project_name='Mock Project').delete()

    # Create the project
    project = Project.objects.create(
        city='TLV',
        project_name='Mock Project',
        project_description='פרויקט מגורים יוקרתי במרכז תל אביב - 8 קומות, 32 דירות',
        phase='CONSTRUCTION'
    )

    print(f"Created project: {project.project_id} - {project.project_name}")

    # Create ProjectDataInputs
    data_inputs, created = ProjectDataInputs.objects.get_or_create(project=project)

    # ============= SECTION 1: Property Details =============
    data_inputs.property_details = {
        'project_description': 'פרויקט מגורים יוקרתי הכולל 32 דירות בבניין בן 8 קומות עם 2 קומות חניה תת קרקעיות. הפרויקט ממוקם בלב תל אביב, ברחוב ויצמן, בסמוך לכיכר המדינה.',
        'property_notes': 'הקרקע נרכשה ב-2023 מחברת נכסים פרטית. כל ההיתרים התקבלו ב-2024.',
        'parcels': [
            {'rights': 'בעלות מלאה', 'block': 7234, 'plot': 45, 'area_cell': 'A', 'main_plan': 'תא/מק/5000', 'land_area': 1200, 'designation': 'מגורים'},
            {'rights': 'בעלות מלאה', 'block': 7234, 'plot': 46, 'area_cell': 'A', 'main_plan': 'תא/מק/5000', 'land_area': 800, 'designation': 'מגורים'}
        ]
    }

    # ============= SECTION 2: Developer Details =============
    data_inputs.developer = {
        'company_name': 'נקטר נדל"ן בע"מ',
        'company_number': '51-234567-8',
        'contacts': [
            {'role': 'מנכ"ל', 'name': 'יוסי כהן', 'phone': '050-1234567', 'email': 'yossi@nectar-realestate.co.il'},
            {'role': 'סמנכ"ל כספים', 'name': 'רחל לוי', 'phone': '050-2345678', 'email': 'rachel@nectar-realestate.co.il'},
            {'role': 'מנהל פרויקט', 'name': 'דוד ישראלי', 'phone': '050-3456789', 'email': 'david@nectar-realestate.co.il'},
            {'role': 'מהנדס', 'name': 'מיכאל אדריכל', 'phone': '050-4567890', 'email': 'michael@architect.co.il'},
            {'role': 'רו"ח', 'name': 'שרה חשב', 'phone': '050-5678901', 'email': 'sara@accounting.co.il'},
            {'role': 'עו"ד', 'name': 'אברהם דין', 'phone': '050-6789012', 'email': 'avraham@law.co.il'}
        ]
    }

    # ============= SECTION 3: Dates =============
    data_inputs.dates = {
        'excavation_permit_date': '2024-01-15',
        'excavation_start_date': '2024-02-01',
        'construction_permit_date': '2024-03-01',
        'construction_start_date': '2024-03-15',
        'construction_duration_months': 36
    }

    # ============= SECTION 4: Planned Area (Garmushka) =============
    planned_area_data = [
        {'building': 'A', 'floor': '-2', 'residential_requested': 0, 'commercial_permit': 0, 'other_main': 0, 'total_main': 0, 'safe_room_residential': 0, 'safe_room_commercial': 0, 'technical_area': 50, 'parking': 800, 'pillar_floor': 0, 'lobby_stairs_residential': 30, 'lobby_stairs_commercial': 0, 'storage': 200, 'laundry_room': 0, 'transformer_room': 30, 'other_secondary': 0, 'total_secondary': 1110, 'gazoztraot': 0, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '-1', 'residential_requested': 0, 'commercial_permit': 0, 'other_main': 0, 'total_main': 0, 'safe_room_residential': 0, 'safe_room_commercial': 0, 'technical_area': 30, 'parking': 800, 'pillar_floor': 0, 'lobby_stairs_residential': 30, 'lobby_stairs_commercial': 0, 'storage': 200, 'laundry_room': 0, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 1060, 'gazoztraot': 0, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': 'קרקע', 'residential_requested': 0, 'commercial_permit': 150, 'other_main': 0, 'total_main': 150, 'safe_room_residential': 0, 'safe_room_commercial': 15, 'technical_area': 0, 'parking': 0, 'pillar_floor': 200, 'lobby_stairs_residential': 80, 'lobby_stairs_commercial': 20, 'storage': 0, 'laundry_room': 0, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 315, 'gazoztraot': 0, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '1', 'residential_requested': 400, 'commercial_permit': 0, 'other_main': 0, 'total_main': 400, 'safe_room_residential': 36, 'safe_room_commercial': 0, 'technical_area': 0, 'parking': 0, 'pillar_floor': 0, 'lobby_stairs_residential': 40, 'lobby_stairs_commercial': 0, 'storage': 0, 'laundry_room': 16, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 92, 'gazoztraot': 24, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '2', 'residential_requested': 400, 'commercial_permit': 0, 'other_main': 0, 'total_main': 400, 'safe_room_residential': 36, 'safe_room_commercial': 0, 'technical_area': 0, 'parking': 0, 'pillar_floor': 0, 'lobby_stairs_residential': 40, 'lobby_stairs_commercial': 0, 'storage': 0, 'laundry_room': 16, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 92, 'gazoztraot': 24, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '3', 'residential_requested': 400, 'commercial_permit': 0, 'other_main': 0, 'total_main': 400, 'safe_room_residential': 36, 'safe_room_commercial': 0, 'technical_area': 0, 'parking': 0, 'pillar_floor': 0, 'lobby_stairs_residential': 40, 'lobby_stairs_commercial': 0, 'storage': 0, 'laundry_room': 16, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 92, 'gazoztraot': 24, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '4', 'residential_requested': 400, 'commercial_permit': 0, 'other_main': 0, 'total_main': 400, 'safe_room_residential': 36, 'safe_room_commercial': 0, 'technical_area': 0, 'parking': 0, 'pillar_floor': 0, 'lobby_stairs_residential': 40, 'lobby_stairs_commercial': 0, 'storage': 0, 'laundry_room': 16, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 92, 'gazoztraot': 24, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '5', 'residential_requested': 400, 'commercial_permit': 0, 'other_main': 0, 'total_main': 400, 'safe_room_residential': 36, 'safe_room_commercial': 0, 'technical_area': 0, 'parking': 0, 'pillar_floor': 0, 'lobby_stairs_residential': 40, 'lobby_stairs_commercial': 0, 'storage': 0, 'laundry_room': 16, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 92, 'gazoztraot': 24, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '6', 'residential_requested': 400, 'commercial_permit': 0, 'other_main': 0, 'total_main': 400, 'safe_room_residential': 36, 'safe_room_commercial': 0, 'technical_area': 0, 'parking': 0, 'pillar_floor': 0, 'lobby_stairs_residential': 40, 'lobby_stairs_commercial': 0, 'storage': 0, 'laundry_room': 16, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 92, 'gazoztraot': 24, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '7', 'residential_requested': 400, 'commercial_permit': 0, 'other_main': 0, 'total_main': 400, 'safe_room_residential': 36, 'safe_room_commercial': 0, 'technical_area': 0, 'parking': 0, 'pillar_floor': 0, 'lobby_stairs_residential': 40, 'lobby_stairs_commercial': 0, 'storage': 0, 'laundry_room': 16, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 92, 'gazoztraot': 24, 'roof_terrace': 0, 'pergola': 0},
        {'building': 'A', 'floor': '8 - גג', 'residential_requested': 200, 'commercial_permit': 0, 'other_main': 0, 'total_main': 200, 'safe_room_residential': 18, 'safe_room_commercial': 0, 'technical_area': 20, 'parking': 0, 'pillar_floor': 0, 'lobby_stairs_residential': 40, 'lobby_stairs_commercial': 0, 'storage': 0, 'laundry_room': 8, 'transformer_room': 0, 'other_secondary': 0, 'total_secondary': 86, 'gazoztraot': 12, 'roof_terrace': 100, 'pergola': 50},
    ]

    # Store planned area in a new JSONField or use existing
    # We'll store it in property_details for now
    data_inputs.property_details['planned_area_data'] = planned_area_data

    # ============= SECTION 5: Financing =============
    data_inputs.financing = {
        'bank': 'LEUMI',
        'financing_body_name': 'בנק לאומי - סניף ליווי פרויקטים',
        'type': 'BANKING',
        'total_funding_amount': 85000000,
        'equity_percentage': 25,
        'funding_agreement_number': 'LEU-2024-12345',
        'funding_agreement_date': '2024-02-15',
        'contacts': [
            {'role': 'מנהל תיק', 'name': 'משה בנקאי', 'phone': '03-1234567', 'email': 'moshe@leumi.co.il'},
            {'role': 'מנהל סיכונים', 'name': 'דנה סיכון', 'phone': '03-2345678', 'email': 'dana@leumi.co.il'},
            {'role': 'מנהל אשראי', 'name': 'יעקב אשראי', 'phone': '03-3456789', 'email': 'yaakov@leumi.co.il'}
        ]
    }

    # ============= SECTION 6: Fixed Rates =============
    data_inputs.fixed_rates = {
        'consumer_price_index': 106.8,
        'construction_input_index': 124.3,
        'developer_profitability_rate': 18.0,
        'vat_rate': 17.0
    }

    # ============= SECTION 7: Revenue Forecast (Apartments Inventory) =============
    # Create 32 apartments across 8 floors (4 per floor)
    apartments = []
    apartment_types = [
        {'type': '3 חדרים', 'rooms': '3', 'area': 80, 'balcony': 12, 'price_per_sqm': 65000},
        {'type': '4 חדרים', 'rooms': '4', 'area': 100, 'balcony': 14, 'price_per_sqm': 62000},
        {'type': '5 חדרים', 'rooms': '5', 'area': 120, 'balcony': 16, 'price_per_sqm': 58000},
        {'type': 'פנטהאוז', 'rooms': '5+', 'area': 150, 'balcony': 20, 'roof_terrace': 50, 'price_per_sqm': 70000},
    ]

    statuses = ['נמכר', 'נמכר', 'נמכר', 'לשיווק', 'לשיווק', 'לשיווק', 'להשכרה', 'תמורה']
    directions = ['צפון', 'דרום', 'מזרח', 'מערב']

    serial = 1
    for floor in range(1, 9):
        for unit in range(1, 5):
            apt_type = apartment_types[unit - 1] if floor < 8 else apartment_types[3]  # Penthouse on top floor

            area = apt_type['area']
            balcony = apt_type['balcony']
            roof_terrace = apt_type.get('roof_terrace', 0) if floor == 8 else 0
            price_per_sqm = apt_type['price_per_sqm']

            # Calculate equivalent area and prices
            equiv_area = area + (balcony * 0.5) + (roof_terrace * 0.3)
            total_with_vat = round(equiv_area * price_per_sqm)
            total_no_vat = round(total_with_vat / 1.17)

            apartments.append({
                'building': 'A',
                'wing': '',
                'floor': str(floor),
                'serial_number': serial,
                'plan_number': f'A-{floor}-{unit}',
                'direction': directions[(unit - 1) % 4],
                'type': apt_type['type'],
                'rooms': apt_type['rooms'],
                'area_main': area,
                'balcony_sun': balcony,
                'roof_terrace': roof_terrace,
                'parking': 1 if unit <= 2 else 2,
                'storage': 1,
                'price_per_sqm_equiv': price_per_sqm,
                'price_per_sqm_main': round(total_with_vat / area),
                'total_value_with_vat': total_with_vat,
                'total_value_no_vat': total_no_vat,
                'status': statuses[serial % len(statuses)]
            })
            serial += 1

    # Commercial spaces
    commercial = [
        {'building': 'A', 'wing': '', 'floor': 'קרקע', 'serial_number': 101, 'plan_number': 'C-1', 'direction': 'צפון', 'property_type': 'חנות', 'sub_type': 'קמעונאות', 'area_net': 50, 'area_gross': 60, 'balcony': 0, 'gallery': 0, 'yard': 15, 'price_per_sqm_no_vat': 35000, 'price_per_sqm_with_vat': 40950, 'total_value_with_vat': 2457000, 'total_value_no_vat': 2100000, 'status': 'לשיווק'},
        {'building': 'A', 'wing': '', 'floor': 'קרקע', 'serial_number': 102, 'plan_number': 'C-2', 'direction': 'דרום', 'property_type': 'חנות', 'sub_type': 'קמעונאות', 'area_net': 80, 'area_gross': 90, 'balcony': 0, 'gallery': 20, 'yard': 0, 'price_per_sqm_no_vat': 32000, 'price_per_sqm_with_vat': 37440, 'total_value_with_vat': 3369600, 'total_value_no_vat': 2880000, 'status': 'נמכר'},
    ]

    data_inputs.revenue_forecast = {
        'revenue_residential': apartments,
        'revenue_commercial': commercial
    }

    # ============= SECTION 8: Cost Forecast =============
    cost_items = [
        {'category': 'קרקע', 'item': 'רכישת קרקע', 'cost_no_vat': 35000000, 'notes': 'רכישה מחברת נכסים פרטית'},
        {'category': 'קרקע', 'item': 'מס רכישה', 'cost_no_vat': 2800000, 'notes': '8% מערך הקרקע'},
        {'category': 'קרקע', 'item': 'עו"ד ורישום', 'cost_no_vat': 350000, 'notes': ''},

        {'category': 'תכנון', 'item': 'אדריכל', 'cost_no_vat': 1800000, 'notes': 'כולל פיקוח עליון'},
        {'category': 'תכנון', 'item': 'קונסטרוקטור', 'cost_no_vat': 600000, 'notes': ''},
        {'category': 'תכנון', 'item': 'יועצים נוספים', 'cost_no_vat': 400000, 'notes': 'חשמל, אינסטלציה, מיזוג'},
        {'category': 'תכנון', 'item': 'סקר קרקע', 'cost_no_vat': 80000, 'notes': ''},

        {'category': 'בנייה', 'item': 'עבודות שלד', 'cost_no_vat': 18000000, 'notes': 'כולל יסודות וקונסטרוקציה'},
        {'category': 'בנייה', 'item': 'עבודות גמר', 'cost_no_vat': 12000000, 'notes': 'ריצוף, צבע, חיפויים'},
        {'category': 'בנייה', 'item': 'מערכות חשמל', 'cost_no_vat': 3500000, 'notes': ''},
        {'category': 'בנייה', 'item': 'מערכות אינסטלציה', 'cost_no_vat': 2500000, 'notes': ''},
        {'category': 'בנייה', 'item': 'מעליות', 'cost_no_vat': 1200000, 'notes': '2 מעליות'},
        {'category': 'בנייה', 'item': 'מיזוג אוויר', 'cost_no_vat': 1500000, 'notes': 'מערכת VRF'},
        {'category': 'בנייה', 'item': 'פיתוח סביבה', 'cost_no_vat': 800000, 'notes': 'גינון, ריצוף, תאורה'},

        {'category': 'היטלים', 'item': 'היטל השבחה', 'cost_no_vat': 2500000, 'notes': ''},
        {'category': 'היטלים', 'item': 'אגרות בנייה', 'cost_no_vat': 600000, 'notes': ''},
        {'category': 'היטלים', 'item': 'חיבור חשמל', 'cost_no_vat': 150000, 'notes': ''},
        {'category': 'היטלים', 'item': 'חיבור מים וביוב', 'cost_no_vat': 100000, 'notes': ''},

        {'category': 'מימון', 'item': 'עמלות בנק', 'cost_no_vat': 850000, 'notes': '1% מהמימון'},
        {'category': 'מימון', 'item': 'ריבית ליווי (משוערת)', 'cost_no_vat': 3000000, 'notes': 'פריים + 1.5%'},

        {'category': 'שיווק', 'item': 'פרסום ושיווק', 'cost_no_vat': 1500000, 'notes': ''},
        {'category': 'שיווק', 'item': 'עמלות מכירה', 'cost_no_vat': 2000000, 'notes': '2% ממכירות'},
        {'category': 'שיווק', 'item': 'דירה לדוגמה', 'cost_no_vat': 400000, 'notes': ''},

        {'category': 'ביטוח', 'item': 'ביטוח קבלנים', 'cost_no_vat': 350000, 'notes': ''},
        {'category': 'ביטוח', 'item': 'ביטוח אחריות מקצועית', 'cost_no_vat': 150000, 'notes': ''},

        {'category': 'ניהול', 'item': 'ניהול פרויקט', 'cost_no_vat': 1200000, 'notes': ''},
        {'category': 'ניהול', 'item': 'פיקוח', 'cost_no_vat': 800000, 'notes': ''},

        {'category': 'עתודות', 'item': 'עתודה לבלת"מ', 'cost_no_vat': 3500000, 'notes': '5% מעלויות הבנייה'},
    ]

    data_inputs.cost_forecast = {
        'cost_forecast_data': cost_items
    }

    # ============= SECTION 9: Construction Classification =============
    data_inputs.construction_classification = {
        'total_sqm_project': 5800,
        'total_sqm_permit': 6200,
        'total_sqm_construction': 8500,
        'direct_construction_cost': 39500000,
        'classification_needed': 'סיווג 100 - קבלן רשום ג"5'
    }

    # ============= SECTION 10: Insurance =============
    data_inputs.insurance = {
        'insurance_components': [
            {'component': 'ביטוח עבודות קבלניות (CAR)', 'amount_no_vat': 250000, 'total_insurance': 250000},
            {'component': 'ביטוח צד ג', 'amount_no_vat': 50000, 'total_insurance': 50000},
            {'component': 'ביטוח אחריות מקצועית', 'amount_no_vat': 50000, 'total_insurance': 50000},
        ]
    }

    # ============= SECTION 11: Guarantees =============
    data_inputs.guarantees = {
        'guarantees_list': [
            {'guarantee_type': 'ערבות ביצוע', 'amount_no_vat': 3950000},
            {'guarantee_type': 'ערבות מכר', 'amount_no_vat': 15000000},
            {'guarantee_type': 'ערבות בנקאית', 'amount_no_vat': 2000000},
        ]
    }

    # ============= SECTION 14: Sensitivity Analysis =============
    total_income = sum(apt['total_value_no_vat'] for apt in apartments) + sum(c['total_value_no_vat'] for c in commercial)
    total_cost = sum(item['cost_no_vat'] for item in cost_items)
    base_profit = total_income - total_cost

    data_inputs.sensitivity_analysis = {
        'base_income': total_income,
        'base_cost': total_cost,
        'base_profit': base_profit,
        'cost_increase_percent': 5,
        'cost_increase_income': total_income,
        'cost_increase_cost': total_cost * 1.05,
        'cost_increase_profit': total_income - (total_cost * 1.05),
        'income_decrease_percent': 5,
        'income_decrease_income': total_income * 0.95,
        'income_decrease_cost': total_cost,
        'income_decrease_profit': (total_income * 0.95) - total_cost,
        'combined_income_percent': -5,
        'combined_cost_percent': 5,
        'combined_income': total_income * 0.95,
        'combined_cost': total_cost * 1.05,
        'combined_profit': (total_income * 0.95) - (total_cost * 1.05)
    }

    # Save all data inputs
    data_inputs.save()
    print("Saved all data input sections")

    # ============= Create Construction Progress =============
    floors = ['כללי', '-2', '-1', 'קרקע', '1', '2', '3', '4', '5', '6', '7', '8']

    construction_tasks = [
        {'task_number': 1, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'התארגנות באתר', 'percent_of_chapter': 0.02, 'percent_of_total': 0.008},
        {'task_number': 2, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'חפירה וביסוס', 'percent_of_chapter': 0.10, 'percent_of_total': 0.04},
        {'task_number': 3, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'יציקת יסודות', 'percent_of_chapter': 0.12, 'percent_of_total': 0.048},
        {'task_number': 4, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'קומת מרתף -2', 'percent_of_chapter': 0.08, 'percent_of_total': 0.032},
        {'task_number': 5, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'קומת מרתף -1', 'percent_of_chapter': 0.08, 'percent_of_total': 0.032},
        {'task_number': 6, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'קומת קרקע', 'percent_of_chapter': 0.08, 'percent_of_total': 0.032},
        {'task_number': 7, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'קומות 1-4', 'percent_of_chapter': 0.24, 'percent_of_total': 0.096},
        {'task_number': 8, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'קומות 5-8', 'percent_of_chapter': 0.24, 'percent_of_total': 0.096},
        {'task_number': 9, 'chapter': 'שלד', 'chapter_weight': 0.40, 'work_item': 'גג ופרגולות', 'percent_of_chapter': 0.04, 'percent_of_total': 0.016},

        {'task_number': 10, 'chapter': 'גמר', 'chapter_weight': 0.30, 'work_item': 'טיח פנים', 'percent_of_chapter': 0.15, 'percent_of_total': 0.045},
        {'task_number': 11, 'chapter': 'גמר', 'chapter_weight': 0.30, 'work_item': 'ריצוף', 'percent_of_chapter': 0.20, 'percent_of_total': 0.06},
        {'task_number': 12, 'chapter': 'גמר', 'chapter_weight': 0.30, 'work_item': 'נגרות', 'percent_of_chapter': 0.15, 'percent_of_total': 0.045},
        {'task_number': 13, 'chapter': 'גמר', 'chapter_weight': 0.30, 'work_item': 'צבע', 'percent_of_chapter': 0.10, 'percent_of_total': 0.03},
        {'task_number': 14, 'chapter': 'גמר', 'chapter_weight': 0.30, 'work_item': 'אלומיניום', 'percent_of_chapter': 0.15, 'percent_of_total': 0.045},
        {'task_number': 15, 'chapter': 'גמר', 'chapter_weight': 0.30, 'work_item': 'חיפויים', 'percent_of_chapter': 0.10, 'percent_of_total': 0.03},
        {'task_number': 16, 'chapter': 'גמר', 'chapter_weight': 0.30, 'work_item': 'מטבחים', 'percent_of_chapter': 0.15, 'percent_of_total': 0.045},

        {'task_number': 17, 'chapter': 'מערכות', 'chapter_weight': 0.20, 'work_item': 'חשמל', 'percent_of_chapter': 0.35, 'percent_of_total': 0.07},
        {'task_number': 18, 'chapter': 'מערכות', 'chapter_weight': 0.20, 'work_item': 'אינסטלציה', 'percent_of_chapter': 0.30, 'percent_of_total': 0.06},
        {'task_number': 19, 'chapter': 'מערכות', 'chapter_weight': 0.20, 'work_item': 'מיזוג', 'percent_of_chapter': 0.20, 'percent_of_total': 0.04},
        {'task_number': 20, 'chapter': 'מערכות', 'chapter_weight': 0.20, 'work_item': 'מעליות', 'percent_of_chapter': 0.15, 'percent_of_total': 0.03},

        {'task_number': 21, 'chapter': 'פיתוח', 'chapter_weight': 0.10, 'work_item': 'פיתוח שטח', 'percent_of_chapter': 0.50, 'percent_of_total': 0.05},
        {'task_number': 22, 'chapter': 'פיתוח', 'chapter_weight': 0.10, 'work_item': 'גינון', 'percent_of_chapter': 0.30, 'percent_of_total': 0.03},
        {'task_number': 23, 'chapter': 'פיתוח', 'chapter_weight': 0.10, 'work_item': 'תאורת חוץ', 'percent_of_chapter': 0.20, 'percent_of_total': 0.02},
    ]

    # Add floor progress to each task (simulating 35% overall completion)
    total_contract = Decimal('39500000')
    for task in construction_tasks:
        task['floor_progress'] = {}

        # Calculate progress based on task order (earlier tasks more complete)
        base_progress = max(0, min(1, 1.0 - (task['task_number'] - 1) * 0.05))

        for floor in floors:
            if task['task_number'] <= 5:
                task['floor_progress'][floor] = base_progress
            elif task['task_number'] <= 9:
                task['floor_progress'][floor] = base_progress * 0.7
            else:
                task['floor_progress'][floor] = base_progress * 0.3

        avg_progress = sum(task['floor_progress'].values()) / len(floors)
        task['total_completion'] = round(avg_progress, 4)
        task['completion_rate'] = round(task['percent_of_total'] * avg_progress, 6)
        task['budgeted_amount'] = float(total_contract * Decimal(str(task['percent_of_total'])))
        task['actual_amount'] = float(Decimal(str(task['budgeted_amount'])) * Decimal(str(avg_progress)))

    overall_completion = sum(t['completion_rate'] for t in construction_tasks) * 100
    total_spent = sum(t['actual_amount'] for t in construction_tasks)

    ConstructionProgress.objects.filter(project=project).delete()
    construction_progress = ConstructionProgress.objects.create(
        project=project,
        total_contract_amount=total_contract,
        available_floors=floors,
        tasks=construction_tasks,
        overall_completion_percentage=Decimal(str(overall_completion)),
        total_spent_to_date=Decimal(str(total_spent))
    )
    print(f"Created construction progress: {overall_completion:.1f}% complete")

    # ============= Create Bank Transactions =============
    # Create a mix of pending, approved, and rejected transactions
    transactions_data = [
        # Equity deposits (approved)
        {'date': '2024-02-01', 'desc': 'הפקדת הון עצמי - סבב ראשון', 'amount': 5000000, 'type': 'CREDIT', 'status': 'APPROVED', 'category': 'OWNER_EQUITY'},
        {'date': '2024-03-15', 'desc': 'הפקדת הון עצמי - סבב שני', 'amount': 3000000, 'type': 'CREDIT', 'status': 'APPROVED', 'category': 'OWNER_EQUITY'},
        {'date': '2024-05-01', 'desc': 'הפקדת הון עצמי - סבב שלישי', 'amount': 2500000, 'type': 'CREDIT', 'status': 'APPROVED', 'category': 'OWNER_EQUITY'},

        # Loan disbursements
        {'date': '2024-03-20', 'desc': 'משיכת הלוואה - שלב א', 'amount': 10000000, 'type': 'CREDIT', 'status': 'APPROVED', 'category': 'LOANS'},
        {'date': '2024-06-15', 'desc': 'משיכת הלוואה - שלב ב', 'amount': 8000000, 'type': 'CREDIT', 'status': 'APPROVED', 'category': 'LOANS'},

        # Sales income
        {'date': '2024-04-01', 'desc': 'תקבול ממכירת דירה A-1-1', 'amount': 4200000, 'type': 'CREDIT', 'status': 'APPROVED', 'category': 'SALES_INCOME'},
        {'date': '2024-05-15', 'desc': 'תקבול ממכירת דירה A-2-2', 'amount': 5500000, 'type': 'CREDIT', 'status': 'APPROVED', 'category': 'SALES_INCOME'},
        {'date': '2024-07-01', 'desc': 'תקבול ממכירת דירה A-3-1', 'amount': 4100000, 'type': 'CREDIT', 'status': 'APPROVED', 'category': 'SALES_INCOME'},

        # Contractor payments (debits)
        {'date': '2024-04-10', 'desc': 'תשלום לקבלן שלד - חשבון 1', 'amount': 2500000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'CONTRACTOR_PAYMENTS'},
        {'date': '2024-05-10', 'desc': 'תשלום לקבלן שלד - חשבון 2', 'amount': 3000000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'CONTRACTOR_PAYMENTS'},
        {'date': '2024-06-10', 'desc': 'תשלום לקבלן שלד - חשבון 3', 'amount': 3500000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'CONTRACTOR_PAYMENTS'},
        {'date': '2024-07-10', 'desc': 'תשלום לקבלן שלד - חשבון 4', 'amount': 2800000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'CONTRACTOR_PAYMENTS'},

        # Supplier payments
        {'date': '2024-05-20', 'desc': 'תשלום לספק ברזל', 'amount': 450000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'SUPPLIER_PAYMENTS'},
        {'date': '2024-06-20', 'desc': 'תשלום לספק בטון', 'amount': 380000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'SUPPLIER_PAYMENTS'},

        # Professional fees
        {'date': '2024-03-01', 'desc': 'שכ"ט אדריכל - מקדמה', 'amount': 500000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'PROFESSIONAL_FEES'},
        {'date': '2024-04-01', 'desc': 'שכ"ט עו"ד', 'amount': 150000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'PROFESSIONAL_FEES'},

        # Bank fees
        {'date': '2024-03-15', 'desc': 'עמלת פתיחת תיק ליווי', 'amount': 85000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'BANK_FEES'},
        {'date': '2024-06-30', 'desc': 'עמלות בנק רבעון 2', 'amount': 12000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'BANK_FEES'},

        # Insurance
        {'date': '2024-03-01', 'desc': 'ביטוח קבלנים - פרמיה שנתית', 'amount': 250000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'INSURANCE'},

        # Permits
        {'date': '2024-02-15', 'desc': 'אגרת היתר בנייה', 'amount': 600000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'PERMITS_FEES'},
        {'date': '2024-03-01', 'desc': 'היטל השבחה - תשלום ראשון', 'amount': 1250000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'PERMITS_FEES'},

        # Marketing
        {'date': '2024-04-01', 'desc': 'קמפיין שיווקי - דיגיטל', 'amount': 200000, 'type': 'DEBIT', 'status': 'APPROVED', 'category': 'MARKETING'},

        # Pending transactions
        {'date': '2024-08-01', 'desc': 'תשלום לקבלן חשמל', 'amount': 450000, 'type': 'DEBIT', 'status': 'PENDING', 'category': 'CONTRACTOR_PAYMENTS'},
        {'date': '2024-08-05', 'desc': 'תקבול ממכירת דירה A-4-3', 'amount': 4800000, 'type': 'CREDIT', 'status': 'PENDING', 'category': 'SALES_INCOME'},
        {'date': '2024-08-10', 'desc': 'תשלום לספק אלומיניום', 'amount': 320000, 'type': 'DEBIT', 'status': 'PENDING', 'category': 'SUPPLIER_PAYMENTS'},
    ]

    for txn in transactions_data:
        BankTransaction.objects.create(
            project=project,
            bank='LEUMI',
            transaction_date=datetime.strptime(txn['date'], '%Y-%m-%d').date(),
            description=txn['desc'],
            amount=Decimal(str(txn['amount'])),
            transaction_type=txn['type'],
            status=txn['status'],
            category=txn['category'],
            is_construction_related=txn['category'] in ['CONTRACTOR_PAYMENTS', 'SUPPLIER_PAYMENTS']
        )

    print(f"Created {len(transactions_data)} bank transactions")

    # ============= Create Equity Deposits =============
    equity_deposits = [
        {'date': '2024-02-01', 'amount': 5000000, 'source': 'TRANSFER', 'desc': 'הפקדה ראשונית לפתיחת תיק ליווי', 'ref': 'EQ-001'},
        {'date': '2024-03-15', 'amount': 3000000, 'source': 'TRANSFER', 'desc': 'הפקדה שנייה לתחילת בנייה', 'ref': 'EQ-002'},
        {'date': '2024-05-01', 'amount': 2500000, 'source': 'TRANSFER', 'desc': 'הפקדה שלישית', 'ref': 'EQ-003'},
        {'date': '2024-07-15', 'amount': 1500000, 'source': 'CHECK', 'desc': 'הפקדה בצ\'ק', 'ref': 'EQ-004'},
    ]

    for deposit in equity_deposits:
        EquityDeposit.objects.create(
            project=project,
            deposit_date=datetime.strptime(deposit['date'], '%Y-%m-%d').date(),
            amount=Decimal(str(deposit['amount'])),
            source=deposit['source'],
            description=deposit['desc'],
            reference_number=deposit['ref']
        )

    print(f"Created {len(equity_deposits)} equity deposits")

    # Calculate and display summary
    total_equity_required = total_cost * Decimal('0.25')
    total_equity_deposited = sum(Decimal(str(d['amount'])) for d in equity_deposits)
    equity_gap = total_equity_required - total_equity_deposited

    print("\n" + "=" * 60)
    print("MOCK PROJECT SUMMARY")
    print("=" * 60)
    print(f"Project ID: {project.project_id}")
    print(f"Project Name: {project.project_name}")
    print(f"Phase: {project.phase}")
    print("-" * 60)
    print(f"Total Revenue (no VAT): ₪{total_income:,.0f}")
    print(f"Total Cost (no VAT): ₪{total_cost:,.0f}")
    print(f"Gross Profit: ₪{base_profit:,.0f}")
    print(f"Profit Margin: {(base_profit/total_income*100):.1f}%")
    print("-" * 60)
    print(f"Construction Progress: {overall_completion:.1f}%")
    print(f"Total Contract: ₪{total_contract:,.0f}")
    print(f"Spent to Date: ₪{total_spent:,.0f}")
    print("-" * 60)
    print(f"Required Equity (25%): ₪{total_equity_required:,.0f}")
    print(f"Deposited Equity: ₪{total_equity_deposited:,.0f}")
    print(f"Equity Gap: ₪{equity_gap:,.0f}")
    print("-" * 60)
    print(f"Apartments: {len(apartments)} units")
    print(f"  - Sold: {len([a for a in apartments if a['status'] == 'נמכר'])}")
    print(f"  - For Sale: {len([a for a in apartments if a['status'] == 'לשיווק'])}")
    print(f"  - For Rent: {len([a for a in apartments if a['status'] == 'להשכרה'])}")
    print(f"Commercial: {len(commercial)} units")
    print("=" * 60)
    print("\nMock project created successfully!")
    print(f"Access at: http://localhost:3001/projects/{project.id}/dashboard")

    return project


if __name__ == '__main__':
    create_mock_project()
