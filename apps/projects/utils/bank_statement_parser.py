"""
Bank Statement Parser for Israeli Banks

Supports parsing of bank statements from multiple Israeli banks:
- Bank Poalim (פועלים)
- Discount Bank (דיסקונט)
- First International Bank (הבינלאומי)
- Bank of Jerusalem (ירושלים)
- Bank Leumi (לאומי)

Each bank has a different format, so we need specific parsers for each.
"""

import pandas as pd
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Tuple


class BankStatementParser:
    """Base class for bank statement parsing"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.bank_name = None
        self.account_number = None

    def _safe_float(self, value) -> float:
        """Convert value to float safely"""
        if pd.isna(value):
            return 0.0
        if isinstance(value, str):
            # Remove commas and other formatting
            value = value.replace(',', '').replace('₪', '').strip()
            try:
                return float(value)
            except (ValueError, AttributeError):
                return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _safe_date(self, value):
        """Convert value to date safely"""
        if pd.isna(value):
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            # Try different date formats
            for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    def _safe_str(self, value) -> str:
        """Convert value to string safely"""
        if pd.isna(value):
            return ''
        return str(value).strip()

    def parse(self) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Parse the bank statement
        Returns: (bank_name, account_number, transactions_list)
        """
        raise NotImplementedError("Each bank parser must implement parse() method")


class PoalimParser(BankStatementParser):
    """Parser for Bank Poalim (פועלים) statements"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.bank_name = 'HAPOALIM'
        self.header_row = 4  # Headers are in row 4

    def parse(self) -> Tuple[str, str, List[Dict[str, Any]]]:
        self.df = pd.read_excel(self.file_path, sheet_name=0, header=None)

        # Extract account number from row 3
        # Format: "מספר חשבון  12-63-8386  לתקופה:  01.03.2025 - 01.09.2025"
        account_info = self._safe_str(self.df.iloc[3, 0])
        match = re.search(r'מספר חשבון\s+([\d\-]+)', account_info)
        if match:
            self.account_number = match.group(1)

        # Headers in row 4: ['תאריך', 'קוד פעולה', 'הפעולה', 'פרטים', 'אסמכתא', 'צרור', 'חובה', 'זכות', "יתרה בש''ח", 'הערה']
        transactions = []
        for row_idx in range(5, len(self.df)):
            row = self.df.iloc[row_idx]

            transaction_date = self._safe_date(row.iloc[0])
            if not transaction_date:
                continue

            debit = self._safe_float(row.iloc[6])  # חובה
            credit = self._safe_float(row.iloc[7])  # זכות
            balance = self._safe_float(row.iloc[8])  # יתרה

            # Determine transaction type and amount
            if credit > 0:
                transaction_type = 'CREDIT'
                amount = credit
            else:
                transaction_type = 'DEBIT'
                amount = debit

            transaction = {
                'transaction_date': transaction_date,
                'value_date': transaction_date,  # Poalim doesn't have separate value date
                'description': f"{self._safe_str(row.iloc[2])} - {self._safe_str(row.iloc[3])}",
                'reference_number': self._safe_str(row.iloc[4]),
                'transaction_type': transaction_type,
                'amount': Decimal(str(amount)),
                'balance': Decimal(str(balance)),
            }
            transactions.append(transaction)

        return self.bank_name, self.account_number, transactions


class DiscountParser(BankStatementParser):
    """Parser for Discount Bank (דיסקונט) statements"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.bank_name = 'DISCOUNT'
        self.header_row = 8  # Headers are in row 8

    def parse(self) -> Tuple[str, str, List[Dict[str, Any]]]:
        self.df = pd.read_excel(self.file_path, sheet_name=0, header=None)

        # Extract account number from row 2
        # Format: "חשבון: 0198175673 | שלום ונתן יזמות בע"מ - סבורה אשדוד"
        account_info = self._safe_str(self.df.iloc[2, 0])
        match = re.search(r'חשבון:\s*(\d+)', account_info)
        if match:
            self.account_number = match.group(1)

        # Headers in row 8: ['תאריך', 'יום ערך', 'תיאור התנועה', '₪ זכות/חובה ', '₪ יתרה ']
        transactions = []
        for row_idx in range(9, len(self.df)):
            row = self.df.iloc[row_idx]

            transaction_date = self._safe_date(row.iloc[0])
            if not transaction_date:
                continue

            value_date = self._safe_date(row.iloc[1])
            description = self._safe_str(row.iloc[2])
            amount_value = self._safe_float(row.iloc[3])  # זכות/חובה (positive = credit, negative = debit)
            balance = self._safe_float(row.iloc[4])

            # Determine transaction type
            if amount_value > 0:
                transaction_type = 'CREDIT'
                amount = amount_value
            else:
                transaction_type = 'DEBIT'
                amount = abs(amount_value)

            transaction = {
                'transaction_date': transaction_date,
                'value_date': value_date,
                'description': description,
                'reference_number': '',
                'transaction_type': transaction_type,
                'amount': Decimal(str(amount)),
                'balance': Decimal(str(balance)),
            }
            transactions.append(transaction)

        return self.bank_name, self.account_number, transactions


class InternationalParser(BankStatementParser):
    """Parser for First International Bank (הבינלאומי) statements"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.bank_name = 'INTERNATIONAL'
        self.header_row = 5  # Headers are in row 5

    def parse(self) -> Tuple[str, str, List[Dict[str, Any]]]:
        self.df = pd.read_excel(self.file_path, sheet_name=0, header=None)

        # Extract account number from row 2
        # Format: "סניף: 126 חשבון: 409069"
        account_info = self._safe_str(self.df.iloc[2, :].tolist())
        match = re.search(r'חשבון:\s*(\d+)', account_info)
        if match:
            self.account_number = match.group(1)

        # Headers in row 5: ['תאריך ערך', 'זכות', 'חובה', 'תאור', 'אסמכתא', 'תאריך ביצוע']
        transactions = []
        for row_idx in range(6, len(self.df)):
            row = self.df.iloc[row_idx]

            value_date = self._safe_date(row.iloc[0])
            if not value_date:
                continue

            credit = self._safe_float(row.iloc[1])  # זכות
            debit = self._safe_float(row.iloc[2])  # חובה
            description = self._safe_str(row.iloc[3])
            reference = self._safe_str(row.iloc[4])
            execution_date = self._safe_date(row.iloc[5])

            # Determine transaction type and amount
            if credit > 0:
                transaction_type = 'CREDIT'
                amount = credit
            else:
                transaction_type = 'DEBIT'
                amount = debit

            transaction = {
                'transaction_date': execution_date if execution_date else value_date,
                'value_date': value_date,
                'description': description,
                'reference_number': reference,
                'transaction_type': transaction_type,
                'amount': Decimal(str(amount)),
                'balance': None,  # International doesn't always show balance
            }
            transactions.append(transaction)

        return self.bank_name, self.account_number, transactions


class JerusalemParser(BankStatementParser):
    """Parser for Bank of Jerusalem (ירושלים) statements"""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.bank_name = 'JERUSALEM'
        self.header_row = 4  # Headers are in row 4

    def parse(self) -> Tuple[str, str, List[Dict[str, Any]]]:
        self.df = pd.read_excel(self.file_path, sheet_name=0, header=None)

        # Extract account number from row 0
        # Format: "עובר ושב, חשבון 051-510474034, ₪, אבן את יסוד גבע"
        account_info = self._safe_str(self.df.iloc[0, 0])
        match = re.search(r'חשבון\s+([\d\-]+)', account_info)
        if match:
            self.account_number = match.group(1)

        # Headers in row 4: ['תאריך', 'תיאור', 'אסמכתא', 'חובה', 'זכות', 'יתרה', ...]
        transactions = []
        for row_idx in range(5, len(self.df)):
            row = self.df.iloc[row_idx]

            transaction_date = self._safe_date(row.iloc[0])
            if not transaction_date:
                continue

            description = self._safe_str(row.iloc[1])
            reference = self._safe_str(row.iloc[2])
            debit = self._safe_float(row.iloc[3])  # חובה
            credit = self._safe_float(row.iloc[4])  # זכות
            balance = self._safe_float(row.iloc[5])  # יתרה
            value_date = self._safe_date(row.iloc[14])  # תאריך ערך

            # Determine transaction type and amount
            if credit > 0:
                transaction_type = 'CREDIT'
                amount = credit
            else:
                transaction_type = 'DEBIT'
                amount = debit

            transaction = {
                'transaction_date': transaction_date,
                'value_date': value_date if value_date else transaction_date,
                'description': description,
                'reference_number': reference,
                'transaction_type': transaction_type,
                'amount': Decimal(str(amount)),
                'balance': Decimal(str(balance)),
            }
            transactions.append(transaction)

        return self.bank_name, self.account_number, transactions


class BankStatementParserFactory:
    """Factory to create appropriate parser based on file content"""

    @staticmethod
    def create_parser(file_path: str) -> BankStatementParser:
        """
        Auto-detect bank type and return appropriate parser
        """
        # Read first few rows to detect bank
        df = pd.read_excel(file_path, sheet_name=0, header=None, nrows=10)

        # Convert to string for pattern matching
        content = ' '.join([str(val) for row in df.values for val in row if pd.notna(val)])

        # Detect bank based on content
        if 'תנועות בחשבון' in content and 'קוד פעולה' in content:
            return PoalimParser(file_path)
        elif 'תנועות בסוג חשבון' in content or 'הבינלאומי' in content:
            return InternationalParser(file_path)
        elif 'עובר ושב' in content:
            # Both Discount and Jerusalem have "עובר ושב"
            # Distinguish by checking row 8 for Discount header pattern
            if len(df) > 8:
                row8_text = ' '.join([str(val) for val in df.iloc[8].values if pd.notna(val)])
                if 'תיאור התנועה' in row8_text and 'יום ערך' in row8_text:
                    return DiscountParser(file_path)

            # Check if it's Jerusalem
            if 'ירושלים' in content:
                return JerusalemParser(file_path)

            # Default to Discount if structure matches (5 columns, "תנועות אחרונות")
            if 'תנועות אחרונות' in content or len(df.columns) == 5:
                return DiscountParser(file_path)
            else:
                return JerusalemParser(file_path)
        else:
            # Try to detect by structure
            if len(df) > 4:
                row4_text = ' '.join([str(val) for val in df.iloc[4].values if pd.notna(val)])
                if 'תאריך' in row4_text and 'זכות' in row4_text and 'חובה' in row4_text:
                    # Could be Poalim or Jerusalem
                    row0_text = ' '.join([str(val) for val in df.iloc[0].values if pd.notna(val)])
                    if 'חשבון' in row0_text:
                        return JerusalemParser(file_path)
                    else:
                        return PoalimParser(file_path)

            raise ValueError("Could not detect bank type from file. Supported banks: Poalim, Discount, International, Jerusalem")

    @staticmethod
    def parse_bank_statement(file_path: str) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Convenience method to auto-detect and parse bank statement
        Returns: (bank_name, account_number, transactions_list)
        """
        parser = BankStatementParserFactory.create_parser(file_path)
        return parser.parse()
