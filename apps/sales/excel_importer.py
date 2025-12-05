"""
Excel Importer for Apartment Inventory
Parses Excel files and imports apartment data into the system
"""
import pandas as pd
from decimal import Decimal, InvalidOperation
from django.db import transaction
from .models import ApartmentInventory, Customer


class ApartmentExcelImporter:
    """Import apartment inventory from Excel files"""

    # Map Hebrew column names to model fields
    RESIDENTIAL_FOR_SALE_COLUMNS = {
        'בניין': 'building_number',
        'אגף': 'wing',
        'קומה': 'floor',
        'מס"ד': 'unit_number',
        'מס\' עפ"י תכנית בקשה': 'plan_number',
        'כיוון': 'unit_direction',
        'סוג': 'unit_type',
        'חדרים': 'room_count',
        'שטח פלדלת במ"ר': 'unit_area_sqm',
        'מרפסת שמש במ"ר': 'balcony_area_sqm',
        'מרפסת גג/חצר במ"ר': 'roof_terrace_area_sqm',
        'חניה': 'parking_spaces',
        'מחסן': 'storage_count',
        'שווי למ"ר אקוו\' כולל מע"מ': 'price_per_sqm_equivalent_with_vat',
        'שווי למ"ר פלדלת כולל מע"מ': 'price_per_sqm_net_with_vat',
        'שווי כולל מע"מ': 'list_price_with_vat',
        'שווי ללא מע"מ\n': 'list_price_no_vat',
        'שווי ללא מע"מ': 'list_price_no_vat',
        'תמורה/ לשיווק/ להשכרה': 'unit_status',
    }

    NON_RESIDENTIAL_COLUMNS = {
        'בניין ': 'building_number',
        'אגף': 'wing',
        'קומה': 'floor',
        'מס"ד': 'unit_number',
        'מס\' עפ"י תכנית בקשה': 'plan_number',
        'כיוון ': 'unit_direction',
        'סוג נכס': 'unit_type',
        'סוג משני': 'unit_sub_type',
        'שטח נטו במ"ר': 'net_area_sqm',
        'שטח ברוטו במ"ר': 'gross_area_sqm',
        'מרפסת  במ"ר': 'terrace_area_sqm',
        'גלריה במ"ר': 'gallery_area_sqm',
        'חצר במ"ר': 'yard_area_sqm',
        'שווי למ"ר לא כולל מע"מ': 'price_per_sqm_no_vat',
        'שווי למ"ר כולל מע"מ': 'price_per_sqm_net_with_vat',
        'שווי כולל מע"מ': 'list_price_with_vat',
        'שווי ללא מע"מ': 'list_price_no_vat',
        'תמורה/ לשיווק/ להשכרה': 'unit_status',
    }

    COMPENSATION_RESIDENTIAL_COLUMNS = {
        'בניין ': 'building_number',
        'אגף': 'wing',
        'קומה': 'floor',
        'מס"ד': 'unit_number',
        'מס\' עפ"י תכנית בקשה': 'plan_number',
        'כיוון ': 'unit_direction',
        'סוג': 'unit_type',
        'חדרים': 'room_count',
        'שטח פלדלת במ"ר': 'unit_area_sqm',
        'מרפסת שמש במ"ר': 'balcony_area_sqm',
        'מרפסת גג/חצר במ"ר': 'roof_terrace_area_sqm',
        'חניה': 'parking_spaces',
        'מחסן ': 'storage_count',
        'שווי למ"ר אקוו\' כולל מע"מ': 'price_per_sqm_equivalent_with_vat',
        'שווי למ"ר פלדלת כולל מע"מ': 'price_per_sqm_net_with_vat',
        'שווי כולל מע"מ, במעוגל': 'list_price_with_vat',
        'שם פרטי ': 'customer_first_name',
        'שם משפחה ': 'customer_last_name',
    }

    # Status mapping
    STATUS_MAPPING = {
        'לשיווק': 'FOR_SALE',
        'נמכר': 'SOLD',
        'תמורה': 'COMPENSATION',
        'להשכרה': 'FOR_RENT',
        'שמור': 'RESERVED',
    }

    # Unit type mapping (Hebrew to English codes)
    UNIT_TYPE_MAPPING = {
        'דירה': 'APARTMENT',
        'פנטהאוז': 'PENTHOUSE',
        'גן': 'GARDEN',
        'דופלקס': 'DUPLEX',
        'מיני פנטהאוז': 'MINI_PENTHOUSE',
        'משרדים': 'OFFICE',
        'מסחר': 'RETAIL',
        'מחסן': 'STORAGE',
        'תעשיה': 'INDUSTRIAL',
        'תעשה קלה': 'LIGHT_INDUSTRIAL',
        'תעשיה קלה': 'LIGHT_INDUSTRIAL',
        'אולם': 'HALL',
        'לוגיסטיקה': 'LOGISTICS',
        'חניה': 'PARKING_REGULAR',
        'חניה רגילה עלית': 'PARKING_ELEVATED',
        'חניה רגילה תת קרקעית': 'PARKING_UNDERGROUND',
        'חניה טורקית': 'PARKING_TANDEM',
        'טורקית (עוקבת)': 'PARKING_TANDEM',
    }

    def __init__(self, project):
        """
        Initialize importer with a project
        Args:
            project: Project instance to which apartments belong
        """
        self.project = project
        self.errors = []
        self.warnings = []
        self.imported_count = 0
        self.skipped_count = 0

    def import_from_file(self, file_path, sheet_name=None):
        """
        Import apartments from Excel file
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name to import (optional)
        Returns:
            dict with results: {'imported': int, 'skipped': int, 'errors': list, 'warnings': list}
        """
        try:
            xl = pd.ExcelFile(file_path)

            if sheet_name:
                sheets_to_process = [sheet_name]
            else:
                # Process all relevant sheets
                sheets_to_process = [s for s in xl.sheet_names if self._is_apartment_sheet(s)]

            for sheet in sheets_to_process:
                self._process_sheet(xl, sheet)

            return {
                'imported': self.imported_count,
                'skipped': self.skipped_count,
                'errors': self.errors,
                'warnings': self.warnings,
            }

        except Exception as e:
            self.errors.append(f"Failed to read Excel file: {str(e)}")
            return {
                'imported': 0,
                'skipped': 0,
                'errors': self.errors,
                'warnings': self.warnings,
            }

    def _is_apartment_sheet(self, sheet_name):
        """Check if sheet contains apartment data"""
        apartment_keywords = ['מלאי', 'תמורות', 'קלט']
        return any(keyword in sheet_name for keyword in apartment_keywords)

    def _process_sheet(self, xl, sheet_name):
        """Process a single sheet"""
        df = pd.read_excel(xl, sheet_name=sheet_name)

        # Remove completely empty rows
        df = df.dropna(how='all')

        # Determine column mapping based on sheet content
        column_mapping = self._detect_column_mapping(df.columns)

        if not column_mapping:
            self.warnings.append(f"Could not detect column structure for sheet '{sheet_name}'")
            return

        # Process each row
        for idx, row in df.iterrows():
            try:
                # Skip rows with missing critical data
                if pd.isna(row.get('בניין')) and pd.isna(row.get('בניין ')):
                    continue

                apartment_data = self._extract_apartment_data(row, column_mapping)

                if apartment_data:
                    self._create_or_update_apartment(apartment_data, idx + 2)  # +2 for Excel row number

            except Exception as e:
                self.errors.append(f"Row {idx + 2}: {str(e)}")
                self.skipped_count += 1

    def _detect_column_mapping(self, columns):
        """Detect which column mapping to use based on available columns"""
        columns_list = columns.tolist()

        # Check for residential for sale
        if 'שטח פלדלת במ"ר' in columns_list and 'תמורה/ לשיווק/ להשכרה' in columns_list:
            return self.RESIDENTIAL_FOR_SALE_COLUMNS

        # Check for non-residential
        if 'סוג נכס' in columns_list:
            return self.NON_RESIDENTIAL_COLUMNS

        # Check for compensation
        if 'שם פרטי ' in columns_list or 'שם משפחה ' in columns_list:
            return self.COMPENSATION_RESIDENTIAL_COLUMNS

        return None

    def _extract_apartment_data(self, row, column_mapping):
        """Extract apartment data from Excel row"""
        data = {'project': self.project}

        for excel_col, model_field in column_mapping.items():
            value = row.get(excel_col)

            if pd.isna(value):
                continue

            # Handle special fields
            if model_field == 'unit_status':
                data[model_field] = self._map_status(str(value).strip())
            elif model_field == 'unit_type':
                data[model_field] = self._map_unit_type(str(value).strip())
            elif model_field in ['building_number', 'unit_number']:
                data[model_field] = str(value).strip()
            elif model_field == 'floor':
                try:
                    data[model_field] = int(float(value))
                except:
                    data[model_field] = 0
            elif 'price' in model_field or 'area' in model_field or 'room' in model_field:
                try:
                    data[model_field] = Decimal(str(value))
                except (InvalidOperation, ValueError):
                    data[model_field] = None
            elif model_field in ['parking_spaces', 'storage_count']:
                try:
                    data[model_field] = int(float(value))
                except:
                    data[model_field] = 0
            else:
                data[model_field] = str(value).strip() if value else ''

        # Required fields validation
        if not data.get('building_number') or data.get('floor') is None:
            return None

        return data

    def _map_status(self, status_hebrew):
        """Map Hebrew status to English code"""
        return self.STATUS_MAPPING.get(status_hebrew, 'FOR_SALE')

    def _map_unit_type(self, type_hebrew):
        """Map Hebrew unit type to English code"""
        return self.UNIT_TYPE_MAPPING.get(type_hebrew, 'OTHER')

    @transaction.atomic
    def _create_or_update_apartment(self, apartment_data, row_number):
        """Create or update apartment in database"""
        try:
            # Check if apartment already exists
            existing = ApartmentInventory.objects.filter(
                project=self.project,
                building_number=apartment_data['building_number'],
                floor=apartment_data['floor'],
                unit_number=apartment_data.get('unit_number', row_number)
            ).first()

            # Handle customer if names are provided
            customer_first = apartment_data.pop('customer_first_name', None)
            customer_last = apartment_data.pop('customer_last_name', None)

            if existing:
                # Update existing
                for key, value in apartment_data.items():
                    setattr(existing, key, value)

                if customer_first or customer_last:
                    existing.customer_first_name = customer_first or ''
                    existing.customer_last_name = customer_last or ''

                existing.save()
            else:
                # Create new
                if not apartment_data.get('unit_number'):
                    apartment_data['unit_number'] = str(row_number)

                apartment = ApartmentInventory(**apartment_data)

                if customer_first or customer_last:
                    apartment.customer_first_name = customer_first or ''
                    apartment.customer_last_name = customer_last or ''

                apartment.save()

            self.imported_count += 1

        except Exception as e:
            self.errors.append(f"Row {row_number}: Failed to save - {str(e)}")
            self.skipped_count += 1


def import_apartments_from_excel(project, file_path, sheet_name=None):
    """
    Convenience function to import apartments
    Args:
        project: Project instance
        file_path: Path to Excel file
        sheet_name: Optional sheet name
    Returns:
        dict with import results
    """
    importer = ApartmentExcelImporter(project)
    return importer.import_from_file(file_path, sheet_name)
