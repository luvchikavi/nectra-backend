from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .income_template import generate_income_template
from .income_calculator import IncomeCalculator
from .excel_parser import parse_income_excel
import json


def download_income_template(request):
    """Generate and download income calculation template"""
    try:
        excel_file = generate_income_template()
        response = HttpResponse(
            excel_file,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=income_template.xlsx'
        return response
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def upload_income_file(request):
    """Upload and process income calculation file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Parse the Excel file
        data = parse_income_excel(uploaded_file)
        
        # Calculate income
        calculator = IncomeCalculator(data)
        results = calculator.calculate_all()
        
        return JsonResponse({
            'success': True,
            'message': 'File processed successfully',
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
