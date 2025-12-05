"""
Utility to parse construction progress Excel files
"""
import pandas as pd
from decimal import Decimal
from typing import Dict, List, Any, Optional


class ConstructionProgressParser:
    """Parser for construction progress Excel files - flexible header detection"""

    # Known header keywords to identify the header row
    HEADER_KEYWORDS = ['מס"ד', 'פרק', 'סעיף עבודה', 'סכום בתקציב', 'כללי']
    # Known floor identifiers
    FLOOR_IDENTIFIERS = ['כללי', '-2', '-1', 'קרקע', '1', '2', '3', '4', '5', '6', '7', '8', 'גג']

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.header_row = None
        self.column_map = {}

    def parse(self) -> Dict[str, Any]:
        """
        Parse the Excel file and return structured data

        Returns:
            Dictionary with:
            - total_contract_amount: float
            - available_floors: list of strings
            - tasks: list of task dictionaries
        """
        # Read Excel file
        self.df = pd.read_excel(self.file_path, header=None)

        # Auto-detect header row
        self.header_row = self._find_header_row()
        if self.header_row is None:
            raise ValueError("Could not find header row in Excel file")

        # Build column mapping
        self._build_column_map()

        # Extract contract amount
        contract_amount = self._extract_contract_amount()

        # Extract floor headers
        available_floors = self._extract_floor_headers()

        # Extract task data
        tasks = self._extract_tasks(available_floors)

        return {
            'total_contract_amount': float(contract_amount),
            'available_floors': available_floors,
            'tasks': tasks
        }

    def _find_header_row(self) -> Optional[int]:
        """Auto-detect the header row by looking for known keywords"""
        for row_idx in range(min(20, len(self.df))):  # Check first 20 rows
            row = self.df.iloc[row_idx]
            row_values = [str(v).strip() if pd.notna(v) else '' for v in row]

            # Count how many header keywords are found
            matches = sum(1 for kw in self.HEADER_KEYWORDS if kw in row_values)
            if matches >= 2:  # At least 2 keywords found
                return row_idx
        return None

    def _build_column_map(self):
        """Build a mapping of column names to indices"""
        row = self.df.iloc[self.header_row]
        for col_idx, val in enumerate(row):
            if pd.notna(val):
                col_name = str(val).strip()
                self.column_map[col_name] = col_idx

    def _get_col_idx(self, *possible_names) -> Optional[int]:
        """Get column index by trying multiple possible names"""
        for name in possible_names:
            if name in self.column_map:
                return self.column_map[name]
        return None

    def _extract_contract_amount(self) -> Decimal:
        """Extract the total contract amount from the file"""
        try:
            # Try to find 'סכום בתקציב' column and sum it
            budget_col = self._get_col_idx('סכום בתקציב', 'סכום')
            if budget_col is not None:
                total = 0
                for row_idx in range(self.header_row + 1, len(self.df)):
                    val = self.df.iloc[row_idx, budget_col]
                    if pd.notna(val):
                        try:
                            total += float(val)
                        except:
                            pass
                return Decimal(str(total))
        except:
            pass
        return Decimal('0')

    def _extract_floor_headers(self) -> List[str]:
        """Extract floor column headers from the header row"""
        floors = []
        row = self.df.iloc[self.header_row]

        for col_idx, val in enumerate(row):
            if pd.notna(val):
                floor_str = str(val).strip()
                # Check if this is a floor identifier
                try:
                    floor_num = float(val)
                    if floor_num == int(floor_num):
                        floor_str = str(int(floor_num))
                except:
                    pass

                if floor_str in self.FLOOR_IDENTIFIERS or floor_str.lstrip('-').isdigit():
                    floors.append(floor_str)

        return floors

    def _safe_float(self, value, default=0.0) -> float:
        """Safely convert value to float"""
        if pd.isna(value):
            return default
        try:
            return float(value)
        except:
            return default

    def _safe_str(self, value, default='') -> str:
        """Safely convert value to string"""
        if pd.isna(value):
            return default
        return str(value).strip()

    def _extract_tasks(self, available_floors: List[str]) -> List[Dict[str, Any]]:
        """Extract all construction tasks from the file"""
        tasks = []

        # Get column indices using flexible mapping
        task_num_col = self._get_col_idx('מס"ד', 'מספר', 'מס\'')
        chapter_col = self._get_col_idx('פרק', 'פרק עבודה')
        chapter_weight_col = self._get_col_idx('משקל פרק (%)', 'משקל פרק', 'משקל')
        work_item_col = self._get_col_idx('סעיף עבודה', 'סעיף', 'תיאור')
        percent_chapter_col = self._get_col_idx('% מהפרק', 'אחוז מהפרק')
        percent_total_col = self._get_col_idx('% מסה"כ', 'אחוז מסהכ')
        budget_col = self._get_col_idx('סכום בתקציב', 'תקציב')
        total_completion_col = self._get_col_idx('סה"כ עד היום', 'סהכ עד היום')
        completion_rate_col = self._get_col_idx('שיעור ביצוע', 'ביצוע %')
        amount_col = self._get_col_idx('סכום', 'סכום בפועל')

        # Build floor column indices
        floor_col_indices = {}
        for floor in available_floors:
            if floor in self.column_map:
                floor_col_indices[floor] = self.column_map[floor]

        # Start from row after header
        for row_idx in range(self.header_row + 1, len(self.df)):
            row = self.df.iloc[row_idx]

            # Check if this is a valid task row (has task number)
            task_number = None
            if task_num_col is not None:
                task_number = row.iloc[task_num_col]

            if pd.isna(task_number):
                continue

            try:
                task_number = int(task_number)
            except:
                continue

            # Extract basic task information using column mapping
            chapter = self._safe_str(row.iloc[chapter_col]) if chapter_col is not None else ''
            chapter_weight = self._safe_float(row.iloc[chapter_weight_col]) if chapter_weight_col is not None else 0
            work_item = self._safe_str(row.iloc[work_item_col]) if work_item_col is not None else ''
            percent_of_chapter = self._safe_float(row.iloc[percent_chapter_col]) if percent_chapter_col is not None else 0
            percent_of_total = self._safe_float(row.iloc[percent_total_col]) if percent_total_col is not None else 0
            budgeted_amount = self._safe_float(row.iloc[budget_col]) if budget_col is not None else 0

            # Extract floor progress using mapped columns
            floor_progress = {}
            for floor_name in available_floors:
                if floor_name in floor_col_indices:
                    col_idx = floor_col_indices[floor_name]
                    progress_val = self._safe_float(row.iloc[col_idx], default=0)
                    floor_progress[floor_name] = progress_val
                else:
                    floor_progress[floor_name] = 0

            # Extract summary columns
            total_completion = self._safe_float(row.iloc[total_completion_col]) if total_completion_col is not None else 0
            completion_rate = self._safe_float(row.iloc[completion_rate_col]) if completion_rate_col is not None else 0
            actual_amount = self._safe_float(row.iloc[amount_col]) if amount_col is not None else 0

            task = {
                'task_number': task_number,
                'chapter': chapter,
                'chapter_weight': chapter_weight,
                'work_item': work_item,
                'percent_of_chapter': percent_of_chapter,
                'percent_of_total': percent_of_total,
                'budgeted_amount': budgeted_amount,
                'floor_progress': floor_progress,
                'total_completion': total_completion,
                'completion_rate': completion_rate,
                'actual_amount': actual_amount,
                'previous_month_progress': 0,  # Optional fields
                'monthly_delta': 0
            }

            tasks.append(task)

        return tasks
