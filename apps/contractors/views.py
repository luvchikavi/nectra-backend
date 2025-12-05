"""
Contractor Module Views
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Contractor, Invoice, InvoiceApproval, ActualCost
from .serializers import (
    ContractorSerializer, ContractorCreateSerializer,
    InvoiceListSerializer, InvoiceDetailSerializer,
    InvoiceCreateSerializer, InvoiceUpdateSerializer,
    InvoiceApprovalSerializer, ActualCostSerializer,
    InvoiceCategoryChoiceSerializer, InvoiceStatusChoiceSerializer
)


class IsContractorOrAdmin(permissions.BasePermission):
    """Permission for contractor or admin access"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Check for contractor profile, staff, or manager/office manager role
        return (
            hasattr(request.user, 'contractor_profile') or
            request.user.is_staff or
            getattr(request.user, 'role', None) in ['TEAM_MANAGER', 'OFFICE_MANAGER']
        )


class IsAdminOrProjectManager(permissions.BasePermission):
    """Permission for admin or project manager only"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Check for staff or manager/office manager role
        return (
            request.user.is_staff or
            getattr(request.user, 'role', None) in ['TEAM_MANAGER', 'OFFICE_MANAGER']
        )


class ContractorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for contractor management (admin only)
    """
    queryset = Contractor.objects.all()
    permission_classes = [IsAdminOrProjectManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['company_name', 'tax_id', 'contact_name', 'email']
    ordering_fields = ['company_name', 'created_at']
    ordering = ['company_name']

    def get_serializer_class(self):
        if self.action == 'create':
            return ContractorCreateSerializer
        return ContractorSerializer

    @action(detail=True, methods=['post'])
    def assign_project(self, request, pk=None):
        """Assign a project to contractor"""
        contractor = self.get_object()
        project_id = request.data.get('project_id')

        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
            contractor.projects.add(project)
            return Response({'status': 'project assigned'})
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_project(self, request, pk=None):
        """Remove a project from contractor"""
        contractor = self.get_object()
        project_id = request.data.get('project_id')

        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contractor.projects.remove(project_id)
        return Response({'status': 'project removed'})


class ContractorProfileViewSet(viewsets.ViewSet):
    """
    ViewSet for contractor's own profile
    """
    permission_classes = [IsContractorOrAdmin]

    def list(self, request):
        """Get current contractor's profile"""
        if not hasattr(request.user, 'contractor_profile'):
            return Response(
                {'error': 'Not a contractor'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ContractorSerializer(request.user.contractor_profile)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def projects(self, request):
        """Get contractor's assigned projects"""
        if not hasattr(request.user, 'contractor_profile'):
            return Response(
                {'error': 'Not a contractor'},
                status=status.HTTP_403_FORBIDDEN
            )

        contractor = request.user.contractor_profile
        from apps.projects.serializers import ProjectSerializer
        projects = contractor.projects.filter(is_active=True)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for invoice management
    - Contractors can CRUD their own invoices
    - Admins can view all and approve/reject
    """
    permission_classes = [IsContractorOrAdmin]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'project', 'contractor']
    search_fields = ['invoice_number', 'vendor_name', 'description']
    ordering_fields = ['created_at', 'invoice_date', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        # Contractors see only their own invoices
        if hasattr(user, 'contractor_profile'):
            return Invoice.objects.filter(contractor=user.contractor_profile)

        # Admins/managers see all invoices
        if user.is_staff or getattr(user, 'role', None) in ['TEAM_MANAGER', 'OFFICE_MANAGER']:
            queryset = Invoice.objects.all()

            # Filter by project if specified
            project_id = self.request.query_params.get('project_id')
            if project_id:
                queryset = queryset.filter(project_id=project_id)

            return queryset

        return Invoice.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        if self.action == 'create':
            return InvoiceCreateSerializer
        if self.action in ['update', 'partial_update']:
            return InvoiceUpdateSerializer
        return InvoiceDetailSerializer

    def perform_create(self, serializer):
        """Set context for serializer - it handles contractor and uploaded_by"""
        # The serializer's create method handles all logic
        serializer.save()

    @action(detail=True, methods=['post'])
    def process_ocr(self, request, pk=None):
        """Trigger OCR processing for invoice"""
        invoice = self.get_object()

        if invoice.status != 'PENDING_OCR':
            return Response(
                {'error': 'Invoice is not pending OCR'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Import and run OCR service
        from .services.ocr_service import process_invoice_ocr
        try:
            result = process_invoice_ocr(invoice)
            return Response(result)
        except Exception as e:
            invoice.status = 'OCR_FAILED'
            invoice.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Submit invoice for admin review"""
        invoice = self.get_object()

        if invoice.status not in ['PENDING_OCR', 'OCR_FAILED', 'PENDING_REVIEW']:
            return Response(
                {'error': 'Invoice cannot be submitted for review'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice.status = 'PENDING_REVIEW'
        invoice.save()
        return Response({'status': 'submitted for review'})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve invoice (admin only)"""
        if not (request.user.is_staff or
                getattr(request.user, 'role', None) in ['TEAM_MANAGER', 'OFFICE_MANAGER']):
            return Response(
                {'error': 'Not authorized to approve'},
                status=status.HTTP_403_FORBIDDEN
            )

        invoice = self.get_object()
        comments = request.data.get('comments', '')

        InvoiceApproval.objects.create(
            invoice=invoice,
            approved_by=request.user,
            action='APPROVE',
            comments=comments
        )

        # Recalculate actual costs
        if invoice.invoice_date:
            ActualCost.recalculate_for_project(
                invoice.project_id,
                invoice.invoice_date.year,
                invoice.invoice_date.month
            )

        serializer = InvoiceDetailSerializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject invoice (admin only)"""
        if not (request.user.is_staff or
                getattr(request.user, 'role', None) in ['TEAM_MANAGER', 'OFFICE_MANAGER']):
            return Response(
                {'error': 'Not authorized to reject'},
                status=status.HTTP_403_FORBIDDEN
            )

        invoice = self.get_object()
        comments = request.data.get('comments', '')

        if not comments:
            return Response(
                {'error': 'Rejection reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        InvoiceApproval.objects.create(
            invoice=invoice,
            approved_by=request.user,
            action='REJECT',
            comments=comments
        )

        serializer = InvoiceDetailSerializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def match_transaction(self, request, pk=None):
        """Match invoice to bank transaction"""
        invoice = self.get_object()
        transaction_id = request.data.get('transaction_id')

        if not transaction_id:
            return Response(
                {'error': 'transaction_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.projects.models import BankTransaction
        try:
            transaction = BankTransaction.objects.get(id=transaction_id)
            invoice.bank_transaction = transaction
            invoice.save()
            return Response({'status': 'transaction matched'})
        except BankTransaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get all invoices pending approval (admin only)"""
        if not (request.user.is_staff or
                getattr(request.user, 'role', None) in ['TEAM_MANAGER', 'OFFICE_MANAGER']):
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )

        invoices = Invoice.objects.filter(status='PENDING_REVIEW')
        project_id = request.query_params.get('project_id')
        if project_id:
            invoices = invoices.filter(project_id=project_id)

        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get invoice category choices"""
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Invoice.INVOICE_CATEGORIES
        ]
        return Response(choices)

    @action(detail=False, methods=['get'])
    def statuses(self, request):
        """Get invoice status choices"""
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Invoice.INVOICE_STATUS
        ]
        return Response(choices)

    @action(detail=False, methods=['get'])
    def suggest_construction_progress(self, request):
        """Suggest construction progress items based on invoice data"""
        project_id = request.query_params.get('project_id')
        search_term = request.query_params.get('q', '')

        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.projects.models import ConstructionProgress
        queryset = ConstructionProgress.objects.filter(project_id=project_id)

        if search_term:
            queryset = queryset.filter(
                Q(section_name__icontains=search_term) |
                Q(chapter__icontains=search_term)
            )

        # Return top 10 suggestions
        results = queryset[:10].values('id', 'section_name', 'chapter', 'weight_percent')
        return Response(list(results))


class InvoiceApprovalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing approval history
    """
    queryset = InvoiceApproval.objects.all()
    serializer_class = InvoiceApprovalSerializer
    permission_classes = [IsContractorOrAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['invoice', 'action', 'approved_by']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        invoice_id = self.request.query_params.get('invoice_id')
        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)
        return queryset


class ActualCostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for actual costs (read-only)
    """
    queryset = ActualCost.objects.all()
    serializer_class = ActualCostSerializer
    permission_classes = [IsAdminOrProjectManager]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['project', 'year', 'month', 'category']
    ordering = ['-year', '-month', 'category']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of actual costs by project"""
        project_id = request.query_params.get('project_id')

        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get totals by category
        totals = ActualCost.objects.filter(
            project_id=project_id
        ).values('category').annotate(
            total_net=Sum('total_net'),
            total_vat=Sum('total_vat'),
            total_gross=Sum('total_gross'),
            total_invoices=Sum('invoice_count')
        )

        # Get monthly breakdown
        monthly = ActualCost.objects.filter(
            project_id=project_id
        ).values('year', 'month').annotate(
            total_net=Sum('total_net'),
            total_vat=Sum('total_vat'),
            total_gross=Sum('total_gross')
        ).order_by('-year', '-month')

        return Response({
            'by_category': list(totals),
            'by_month': list(monthly)
        })

    @action(detail=False, methods=['post'])
    def recalculate(self, request):
        """Recalculate actual costs for a project/period"""
        project_id = request.data.get('project_id')
        year = request.data.get('year')
        month = request.data.get('month')

        if not all([project_id, year, month]):
            return Response(
                {'error': 'project_id, year, and month are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ActualCost.recalculate_for_project(project_id, year, month)
        return Response({'status': 'recalculated'})
