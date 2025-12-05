"""
OCR Service for Invoice Processing
Uses EasyOCR for Hebrew/English text extraction
"""
import re
import os
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not installed. OCR functionality will be limited.")

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


class InvoiceOCRProcessor:
    """
    Process invoices using OCR to extract key fields:
    - Invoice number
    - Invoice date
    - Vendor name and tax ID
    - Amounts (net, VAT, total)
    """

    def __init__(self):
        self.reader = None
        if EASYOCR_AVAILABLE:
            # Initialize EasyOCR with Hebrew and English
            self.reader = easyocr.Reader(['he', 'en'], gpu=False)

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process an invoice file and extract data

        Args:
            file_path: Path to the invoice file (PDF or image)

        Returns:
            Dictionary with extracted data and confidence scores
        """
        if not self.reader:
            raise RuntimeError("EasyOCR is not available. Please install it with: pip install easyocr")

        # Get file extension
        _, ext = os.path.splitext(file_path.lower())

        # Convert PDF to images if needed
        if ext == '.pdf':
            if not PDF2IMAGE_AVAILABLE:
                raise RuntimeError("pdf2image is not available. Please install it.")
            images = pdf2image.convert_from_path(file_path, first_page=1, last_page=1)
            if not images:
                raise ValueError("Could not convert PDF to image")
            # Save first page as temp image
            temp_path = file_path + '_temp.png'
            images[0].save(temp_path, 'PNG')
            file_to_process = temp_path
        else:
            file_to_process = file_path

        try:
            # Run OCR
            results = self.reader.readtext(file_to_process)

            # Extract text and confidence
            extracted_text = []
            total_confidence = 0

            for (bbox, text, confidence) in results:
                extracted_text.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
                total_confidence += confidence

            avg_confidence = total_confidence / len(results) if results else 0

            # Parse the extracted text to find invoice fields
            parsed_data = self._parse_invoice_data(extracted_text)
            parsed_data['raw_ocr'] = extracted_text
            parsed_data['confidence'] = round(avg_confidence * 100, 2)

            return parsed_data

        finally:
            # Clean up temp file if created
            if ext == '.pdf' and os.path.exists(file_to_process):
                os.remove(file_to_process)

    def _parse_invoice_data(self, ocr_results: list) -> Dict[str, Any]:
        """
        Parse OCR results to extract invoice fields
        """
        # Combine all text for pattern matching
        full_text = ' '.join([item['text'] for item in ocr_results])

        result = {
            'invoice_number': self._extract_invoice_number(full_text, ocr_results),
            'invoice_date': self._extract_date(full_text, ocr_results),
            'vendor_name': self._extract_vendor_name(ocr_results),
            'vendor_tax_id': self._extract_tax_id(full_text),
            'net_amount': None,
            'vat_amount': None,
            'total_amount': None,
        }

        # Extract amounts
        amounts = self._extract_amounts(full_text, ocr_results)
        result.update(amounts)

        return result

    def _extract_invoice_number(self, full_text: str, ocr_results: list) -> Optional[str]:
        """Extract invoice number from text"""
        # Common patterns for invoice numbers in Hebrew and English
        patterns = [
            r'חשבונית\s*(?:מס[\'"]?\s*)?[:#]?\s*(\d+)',  # Hebrew: חשבונית מס' 12345
            r'invoice\s*(?:no|number|#)?[.:\s]*(\d+)',  # English: Invoice No. 12345
            r'מס[\'"]?\s*חשבונית[:\s]*(\d+)',  # Hebrew: מס' חשבונית: 12345
            r'(?:אסמכתא|מסמך)\s*[:#]?\s*(\d+)',  # Hebrew: אסמכתא/מסמך
        ]

        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_date(self, full_text: str, ocr_results: list) -> Optional[str]:
        """Extract invoice date from text"""
        # Date patterns
        patterns = [
            r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})',  # YYYY/MM/DD
        ]

        for pattern in patterns:
            match = re.search(pattern, full_text)
            if match:
                groups = match.groups()
                try:
                    if len(groups[0]) == 4:  # YYYY-MM-DD format
                        year, month, day = groups
                    else:  # DD-MM-YYYY format
                        day, month, year = groups

                    # Handle 2-digit years
                    if len(year) == 2:
                        year = '20' + year

                    # Validate and return ISO format
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_vendor_name(self, ocr_results: list) -> Optional[str]:
        """Extract vendor name - usually at the top of the invoice"""
        if not ocr_results:
            return None

        # Look for company name indicators
        for i, item in enumerate(ocr_results[:10]):  # Check first 10 items
            text = item['text']
            # Look for company suffixes
            if any(suffix in text for suffix in ['בע"מ', 'בעמ', 'Ltd', 'LTD', 'Inc']):
                return text
            # Look for business registration patterns
            if re.search(r'ח\.?פ\.?|עוסק\s*מורשה', text):
                # Previous item might be the name
                if i > 0:
                    return ocr_results[i-1]['text']

        # Return first substantial text as fallback
        for item in ocr_results[:5]:
            if len(item['text']) > 3 and item['confidence'] > 0.5:
                return item['text']

        return None

    def _extract_tax_id(self, full_text: str) -> Optional[str]:
        """Extract Israeli tax ID (ח.פ. or עוסק מורשה)"""
        patterns = [
            r'ח\.?פ\.?\s*[:#]?\s*(\d{9})',  # ח.פ.: 123456789
            r'עוסק\s*מורשה\s*[:#]?\s*(\d{9})',  # עוסק מורשה: 123456789
            r'(?:vat|tax)\s*(?:id|no|number)?[:\s]*(\d{9})',  # VAT ID: 123456789
        ]

        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_amounts(self, full_text: str, ocr_results: list) -> Dict[str, Optional[Decimal]]:
        """Extract monetary amounts from invoice"""
        amounts = {
            'net_amount': None,
            'vat_amount': None,
            'total_amount': None,
        }

        # Amount patterns with Hebrew and English labels
        amount_patterns = {
            'net_amount': [
                r'(?:סכום|סה"כ)\s*(?:לפני\s*מע"מ|נטו)[:\s]*([\d,]+(?:\.\d{2})?)',
                r'(?:subtotal|net)[:\s]*([\d,]+(?:\.\d{2})?)',
            ],
            'vat_amount': [
                r'מע"מ\s*(?:\d+%)?[:\s]*([\d,]+(?:\.\d{2})?)',
                r'(?:vat|tax)\s*(?:\d+%)?[:\s]*([\d,]+(?:\.\d{2})?)',
            ],
            'total_amount': [
                r'(?:סה"כ\s*(?:לתשלום|כולל)|סך\s*הכל)[:\s]*([\d,]+(?:\.\d{2})?)',
                r'(?:total|grand\s*total)[:\s]*([\d,]+(?:\.\d{2})?)',
            ],
        }

        for field, patterns in amount_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    try:
                        # Remove commas and convert to Decimal
                        amount_str = match.group(1).replace(',', '')
                        amounts[field] = Decimal(amount_str)
                        break
                    except (InvalidOperation, ValueError):
                        continue

        # If we have net and VAT but not total, calculate it
        if amounts['net_amount'] and amounts['vat_amount'] and not amounts['total_amount']:
            amounts['total_amount'] = amounts['net_amount'] + amounts['vat_amount']

        # If we have total and VAT but not net, calculate it
        if amounts['total_amount'] and amounts['vat_amount'] and not amounts['net_amount']:
            amounts['net_amount'] = amounts['total_amount'] - amounts['vat_amount']

        # If we have total and net but not VAT, calculate it
        if amounts['total_amount'] and amounts['net_amount'] and not amounts['vat_amount']:
            amounts['vat_amount'] = amounts['total_amount'] - amounts['net_amount']

        return amounts


def process_invoice_ocr(invoice) -> Dict[str, Any]:
    """
    Process an invoice instance through OCR

    Args:
        invoice: Invoice model instance

    Returns:
        Dictionary with extracted data
    """
    processor = InvoiceOCRProcessor()

    # Get file path
    file_path = invoice.original_file.path

    try:
        # Process the file
        result = processor.process_file(file_path)

        # Update invoice with extracted data
        if result.get('invoice_number'):
            invoice.invoice_number = result['invoice_number']
        if result.get('invoice_date'):
            invoice.invoice_date = result['invoice_date']
        if result.get('vendor_name'):
            invoice.vendor_name = result['vendor_name']
        if result.get('vendor_tax_id'):
            invoice.vendor_tax_id = result['vendor_tax_id']
        if result.get('net_amount'):
            invoice.net_amount = result['net_amount']
        if result.get('vat_amount'):
            invoice.vat_amount = result['vat_amount']
        if result.get('total_amount'):
            invoice.total_amount = result['total_amount']

        # Store raw OCR data
        invoice.ocr_raw_data = result.get('raw_ocr', [])
        invoice.ocr_confidence = Decimal(str(result.get('confidence', 0)))

        # Update status
        invoice.status = 'PENDING_REVIEW'
        invoice.save()

        return {
            'success': True,
            'extracted_data': {
                'invoice_number': result.get('invoice_number'),
                'invoice_date': result.get('invoice_date'),
                'vendor_name': result.get('vendor_name'),
                'vendor_tax_id': result.get('vendor_tax_id'),
                'net_amount': str(result.get('net_amount')) if result.get('net_amount') else None,
                'vat_amount': str(result.get('vat_amount')) if result.get('vat_amount') else None,
                'total_amount': str(result.get('total_amount')) if result.get('total_amount') else None,
            },
            'confidence': result.get('confidence', 0),
            'message': 'OCR processing completed successfully'
        }

    except Exception as e:
        logger.error(f"OCR processing failed for invoice {invoice.id}: {str(e)}")
        invoice.status = 'OCR_FAILED'
        invoice.save()
        raise
