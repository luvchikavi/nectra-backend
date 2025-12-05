from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.http import FileResponse
from django.db import transaction
import pandas as pd
from decimal import Decimal
import os

from .models import ApartmentInventory
from apps.projects.models import Project


@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_apartment_inventory(request, project_id):
    """
    Upload apartment inventory from Excel template
    POST /api/projects/{project_id}/apartments/upload/
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    excel_file = request.FILES['file']
    
    if not excel_file.name.endswith(('.xlsx', '.xls')):
        return Response(
            {'error': 'Invalid file type. Please upload Excel file (.xlsx or .xls)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Apartment_Inventory')
        df_data = df[df['Unit #\nמס"ד'].notna()].copy()
        
        if len(df_data) == 0:
            return Response({'error': 'No data found in Excel file'}, status=status.HTTP_400_BAD_REQUEST)
        
        apartments_data = []
        errors = []
        
        for idx, row in df_data.iterrows():
            try:
                room_type_str = str(row.get('Room Type\nסוג יחידה', '')).strip()
                room_count = row.get('Rooms\nמס\' חדרים', 0)
                
                unit_type = 'APARTMENT'
                if 'פנט' in room_type_str or 'penthouse' in room_type_str.lower():
                    unit_type = 'PENTHOUSE'
                elif 'גן' in room_type_str or 'garden' in room_type_str.lower():
                    unit_type = 'GARDEN'
                elif 'דופלקס' in room_type_str or 'duplex' in room_type_str.lower():
                    unit_type = 'DUPLEX'
                
                status_str = str(row.get('Status\nסטטוס', 'Available')).strip()
                status_map = {
                    'Available': 'AVAILABLE', 'זמין': 'AVAILABLE',
                    'Reserved': 'RESERVED', 'שמור': 'RESERVED',
                    'Sold': 'SOLD', 'נמכר': 'SOLD',
                    'Owner': 'OWNER', 'בעלים': 'OWNER',
                    'Unavailable': 'UNAVAILABLE', 'לא זמין': 'UNAVAILABLE',
                    'Rented': 'RENTED', 'מושכר': 'RENTED',
                }
                unit_status = status_map.get(status_str, 'AVAILABLE')
                
                floor_val = row.get('Floor\nקומה', '')
                if str(floor_val).strip() == 'קרקע':
                    floor = 0
                else:
                    floor = int(floor_val) if floor_val else 0
                
                apartment_data = {
                    'project': project,
                    'building_number': int(row.get('Building\nבניין', 1)),
                    'floor': floor,
                    'unit_number': int(row['Unit #\nמס"ד']),
                    'unit_type': unit_type,
                    'room_count': Decimal(str(room_count)),
                    'unit_direction': str(row.get('Direction\nכיוון', '')).strip(),
                    'unit_area_sqm': Decimal(str(row.get('Unit Area (sqm)\nשטח פלדלת', 0))),
                    'balcony_area_sqm': Decimal(str(row.get('Balcony (sqm)\nמרפסת שמש', 0) or 0)),
                    'garden_area_sqm': Decimal(str(row.get('Garden/Roof (sqm)\nמרפסת גג/חצר', 0) or 0)),
                    'storage_area_sqm': Decimal(str(row.get('Storage (sqm)\nמחסן', 0) or 0)),
                    'parking_spaces': int(row.get('Parking\nחניות', 0) or 0),
                    'list_price_no_vat': Decimal(str(row.get('Total NO VAT\nסה"כ ללא מע"ם', 0))),
                    'vat_rate': Decimal(str(row.get('VAT Rate\nשיעור מע"מ', 0.17))),
                    'final_price_no_vat': Decimal(str(row.get('Total NO VAT\nסה"כ ללא מע"ם', 0))),
                    'unit_status': unit_status,
                    'customer_name': str(row.get('Customer Name\nשם לקוח', '')).strip(),
                    'customer_id_number': str(row.get('Customer ID\nת.ז. לקוח', '')).strip(),
                }
                
                apartments_data.append(apartment_data)
                
            except Exception as e:
                errors.append({'row': idx + 2, 'error': str(e)})
        
        if errors:
            return Response({
                'error': 'Validation errors found',
                'errors': errors,
                'valid_rows': len(apartments_data),
                'total_rows': len(df_data)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        action = request.data.get('action', 'preview')
        
        if action == 'preview':
            return Response({
                'status': 'preview',
                'message': f'Ready to import {len(apartments_data)} apartments',
                'total_count': len(apartments_data)
            })
        
        elif action == 'save':
            with transaction.atomic():
                replace_existing = request.data.get('replace_existing', False)
                if replace_existing:
                    ApartmentInventory.objects.filter(project=project).delete()
                
                created_apartments = []
                for apt_data in apartments_data:
                    apartment = ApartmentInventory.objects.create(**apt_data)
                    created_apartments.append(apartment)
                
                return Response({
                    'status': 'success',
                    'message': f'Successfully imported {len(created_apartments)} apartments',
                    'created_count': len(created_apartments),
                    'project_id': project.id,
                    'project_name': project.project_name
                }, status=status.HTTP_201_CREATED)
        
        else:
            return Response({'error': 'Invalid action. Use "preview" or "save"'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'error': f'Error processing file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def download_apartment_template(request):
    """
    Download the standardized Excel template
    GET /api/apartments/template/
    """
    template_path = '/app/templates/Apartment_Inventory_Template.xlsx'
    
    if os.path.exists(template_path):
        return FileResponse(
            open(template_path, 'rb'),
            as_attachment=True,
            filename='Apartment_Inventory_Template.xlsx'
        )
    else:
        return Response({'error': 'Template file not found'}, status=status.HTTP_404_NOT_FOUND)
