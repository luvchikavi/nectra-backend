"""
Apartment Inventory Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import tempfile
import os

from apps.sales.models import ApartmentInventory
from apps.sales.serializers import (
    ApartmentInventorySerializer,
    ApartmentInventoryListSerializer,
    ApartmentInventoryDetailSerializer,
)
from apps.sales.excel_importer import ApartmentExcelImporter


class ApartmentInventoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for apartment inventory management

    List endpoint returns simplified data for grid view
    Retrieve endpoint returns full details
    """
    queryset = ApartmentInventory.objects.select_related('project', 'customer').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Filtering
    filterset_fields = {
        'project': ['exact'],
        'unit_status': ['exact'],
        'unit_type': ['exact'],
        'building_number': ['exact'],
        'floor': ['exact', 'gte', 'lte'],
        'room_count': ['exact', 'gte', 'lte'],
        'list_price_with_vat': ['gte', 'lte'],
    }

    # Search
    search_fields = [
        'unit_unique_id',
        'unit_number',
        'building_number',
        'customer_first_name',
        'customer_last_name',
    ]

    # Ordering
    ordering_fields = [
        'building_number',
        'floor',
        'unit_number',
        'list_price_with_vat',
        'room_count',
        'created_at',
    ]
    ordering = ['building_number', 'floor', 'unit_number']

    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return ApartmentInventoryListSerializer
        elif self.action == 'retrieve':
            return ApartmentInventoryDetailSerializer
        return ApartmentInventorySerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for apartments"""
        queryset = self.filter_queryset(self.get_queryset())

        total = queryset.count()

        # Count by status
        status_counts = {}
        for status_code, status_name in ApartmentInventory.UNIT_STATUS:
            count = queryset.filter(unit_status=status_code).count()
            if count > 0:
                status_counts[status_code] = {
                    'name': status_name,
                    'count': count,
                    'percentage': round((count / total * 100), 1) if total > 0 else 0
                }

        # Count by type
        type_counts = {}
        for type_code, type_name in ApartmentInventory.UNIT_TYPES:
            count = queryset.filter(unit_type=type_code).count()
            if count > 0:
                type_counts[type_code] = {
                    'name': type_name,
                    'count': count,
                    'percentage': round((count / total * 100), 1) if total > 0 else 0
                }

        # Price statistics
        apts_with_price = queryset.exclude(list_price_with_vat__isnull=True)
        price_stats = {}
        if apts_with_price.exists():
            from django.db.models import Sum, Avg, Min, Max
            aggregates = apts_with_price.aggregate(
                total=Sum('list_price_with_vat'),
                average=Avg('list_price_with_vat'),
                min=Min('list_price_with_vat'),
                max=Max('list_price_with_vat'),
            )
            price_stats = {
                'total_value': float(aggregates['total']) if aggregates['total'] else 0,
                'average_price': float(aggregates['average']) if aggregates['average'] else 0,
                'min_price': float(aggregates['min']) if aggregates['min'] else 0,
                'max_price': float(aggregates['max']) if aggregates['max'] else 0,
            }

        return Response({
            'total_apartments': total,
            'by_status': status_counts,
            'by_type': type_counts,
            'price_statistics': price_stats,
        })

    @action(detail=True, methods=['post'])
    def mark_sold(self, request, pk=None):
        """Mark apartment as sold (will create sales transaction in future)"""
        apartment = self.get_object()

        if apartment.unit_status == 'SOLD':
            return Response(
                {'error': 'Apartment is already sold'},
                status=status.HTTP_400_BAD_REQUEST
            )

        apartment.unit_status = 'SOLD'
        apartment.save()

        serializer = self.get_serializer(apartment)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available apartments (for sale)"""
        queryset = self.get_queryset().filter(unit_status='FOR_SALE')
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_excel(self, request):
        """
        Upload apartment inventory from Excel file
        POST /api/v1/sales/apartments/upload_excel/

        Expects:
        - file: Excel file with Hebrew column headers
        - project_id: ID of the project to associate apartments with
        """
        from apps.projects.models import Project

        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES['file']
        project_id = request.data.get('project_id')

        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {'error': f'Project with id {project_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        try:
            # Use the existing Excel importer with Hebrew column mappings
            importer = ApartmentExcelImporter(project)
            result = importer.import_from_file(tmp_file_path)

            return Response({
                'status': 'success',
                'message': f'Successfully imported {result["imported"]} apartments',
                'imported': result['imported'],
                'skipped': result['skipped'],
                'errors': result['errors'],
                'warnings': result['warnings'],
            }, status=status.HTTP_201_CREATED if result['imported'] > 0 else status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Error processing Excel file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
