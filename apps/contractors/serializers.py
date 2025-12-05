"""
Contractor Module Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Contractor, Invoice, InvoiceApproval, ActualCost

User = get_user_model()


class ContractorSerializer(serializers.ModelSerializer):
    """Serializer for contractor profile"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    project_ids = serializers.PrimaryKeyRelatedField(
        source='projects',
        many=True,
        read_only=True
    )

    class Meta:
        model = Contractor
        fields = [
            'id', 'user', 'user_email', 'company_name', 'tax_id',
            'contact_name', 'phone', 'email', 'address',
            'project_ids', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ContractorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contractor with user account"""
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    user_email = serializers.EmailField(write_only=True)
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        default=[]
    )

    class Meta:
        model = Contractor
        fields = [
            'username', 'password', 'user_email',
            'company_name', 'tax_id', 'contact_name',
            'phone', 'email', 'address', 'project_ids'
        ]

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        user_email = validated_data.pop('user_email')
        project_ids = validated_data.pop('project_ids', [])

        # Create user account
        user = User.objects.create_user(
            username=username,
            email=user_email,
            password=password,
            role='contractor'
        )

        # Create contractor profile
        contractor = Contractor.objects.create(
            user=user,
            **validated_data
        )

        # Assign projects
        if project_ids:
            from apps.projects.models import Project
            projects = Project.objects.filter(id__in=project_ids)
            contractor.projects.set(projects)

        return contractor


class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for invoice list views"""
    contractor_name = serializers.CharField(
        source='contractor.company_name',
        read_only=True,
        allow_null=True
    )
    project_name = serializers.CharField(
        source='project.project_name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_date', 'vendor_name',
            'total_amount', 'status', 'status_display',
            'category', 'category_display',
            'contractor_name', 'project_name', 'created_at'
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Full serializer for invoice details"""
    contractor_name = serializers.CharField(
        source='contractor.company_name',
        read_only=True,
        allow_null=True
    )
    project_name = serializers.CharField(
        source='project.project_name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name',
        read_only=True
    )
    construction_progress_name = serializers.CharField(
        source='construction_progress.section_name',
        read_only=True
    )
    approvals = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'contractor', 'contractor_name',
            'project', 'project_name',
            'invoice_number', 'invoice_date', 'due_date',
            'vendor_name', 'vendor_tax_id',
            'net_amount', 'vat_amount', 'total_amount',
            'category', 'category_display',
            'construction_progress', 'construction_progress_name',
            'bank_transaction',
            'status', 'status_display',
            'original_file', 'ocr_raw_data', 'ocr_confidence',
            'description', 'notes',
            'uploaded_by', 'uploaded_by_name',
            'approvals',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'ocr_raw_data', 'ocr_confidence',
            'uploaded_by', 'created_at', 'updated_at'
        ]

    def get_approvals(self, obj):
        return InvoiceApprovalSerializer(
            obj.approvals.all()[:5],
            many=True
        ).data


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for contractor invoice upload and manual entry"""
    # Make original_file optional to support manual entry
    original_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Invoice
        fields = [
            'project', 'original_file', 'description', 'notes',
            # Fields for manual entry
            'invoice_number', 'invoice_date', 'due_date',
            'vendor_name', 'vendor_tax_id',
            'net_amount', 'vat_amount', 'total_amount',
            'category', 'status'
        ]
        extra_kwargs = {
            'invoice_number': {'required': False},
            'invoice_date': {'required': False},
            'due_date': {'required': False},
            'vendor_name': {'required': False},
            'vendor_tax_id': {'required': False},
            'net_amount': {'required': False},
            'vat_amount': {'required': False},
            'total_amount': {'required': False},
            'category': {'required': False},
            'status': {'required': False},
        }

    def create(self, validated_data):
        request = self.context.get('request')

        # Determine status based on whether it's a file upload or manual entry
        if 'status' not in validated_data or not validated_data.get('status'):
            if validated_data.get('original_file'):
                validated_data['status'] = 'PENDING_OCR'
            else:
                validated_data['status'] = 'PENDING_REVIEW'

        # Set contractor if user has contractor_profile
        try:
            contractor_profile = request.user.contractor_profile
            validated_data['contractor'] = contractor_profile
        except (Contractor.DoesNotExist, AttributeError):
            # Admin users without contractor profile - contractor will be null
            pass

        validated_data['uploaded_by'] = request.user

        invoice = Invoice.objects.create(**validated_data)
        return invoice


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating invoice details (after OCR or manual edit)"""

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'invoice_date', 'due_date',
            'vendor_name', 'vendor_tax_id',
            'net_amount', 'vat_amount', 'total_amount',
            'category', 'construction_progress',
            'description', 'notes'
        ]

    def validate(self, data):
        instance = self.instance
        if instance and not instance.can_be_edited:
            raise serializers.ValidationError(
                "Cannot edit an approved or paid invoice"
            )
        return data


class InvoiceApprovalSerializer(serializers.ModelSerializer):
    """Serializer for invoice approval records"""
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True
    )
    action_display = serializers.CharField(
        source='get_action_display',
        read_only=True
    )

    class Meta:
        model = InvoiceApproval
        fields = [
            'id', 'invoice', 'approved_by', 'approved_by_name',
            'action', 'action_display', 'comments', 'created_at'
        ]
        read_only_fields = ['id', 'approved_by', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['approved_by'] = request.user
        return super().create(validated_data)


class ActualCostSerializer(serializers.ModelSerializer):
    """Serializer for actual costs aggregation"""
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    project_name = serializers.CharField(
        source='project.name',
        read_only=True
    )

    class Meta:
        model = ActualCost
        fields = [
            'id', 'project', 'project_name',
            'year', 'month', 'category', 'category_display',
            'total_net', 'total_vat', 'total_gross',
            'invoice_count', 'last_updated'
        ]


class InvoiceCategoryChoiceSerializer(serializers.Serializer):
    """Serializer for invoice category choices"""
    value = serializers.CharField()
    label = serializers.CharField()


class InvoiceStatusChoiceSerializer(serializers.Serializer):
    """Serializer for invoice status choices"""
    value = serializers.CharField()
    label = serializers.CharField()
