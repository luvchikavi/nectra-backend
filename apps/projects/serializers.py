from rest_framework import serializers
from .models import Project, ProjectDataInputs, ConstructionProgress, ConstructionProgressSnapshot, BankTransaction, EquityDeposit, ProjectDocument


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    phase_display = serializers.CharField(source='get_phase_display', read_only=True)
    apartments_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'project_id',
            'city',
            'city_display',
            'project_name',
            'project_description',
            'phase',
            'phase_display',
            'is_active',
            'deleted_at',
            'apartments_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['project_id', 'is_active', 'deleted_at', 'created_at', 'updated_at']

    def get_apartments_count(self, obj):
        """Get the count of apartments for this project - from ApartmentInventory or Section 7 data"""
        try:
            # First try ApartmentInventory
            count = obj.apartments.count()
            if count > 0:
                return count

            # Fallback to Section 7 (revenue_forecast) data
            try:
                data_inputs = obj.data_inputs
                revenue_forecast = data_inputs.revenue_forecast or {}
                revenue_residential = revenue_forecast.get('revenue_residential', [])
                if revenue_residential and len(revenue_residential) > 0:
                    return len(revenue_residential)
            except:
                pass

            return 0
        except:
            return 0


class ProjectDataInputsSerializer(serializers.ModelSerializer):
    """Serializer for ProjectDataInputs model"""
    project_id = serializers.CharField(source='project.project_id', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = ProjectDataInputs
        fields = [
            'id',
            'project',
            'project_id',
            'project_name',
            # New 14 fields
            'property_details',
            'dates',
            'developer',
            'financing',
            'profitability',
            'land_value',
            'fixed_rates',
            'insurance',
            'construction_classification',
            'guarantees',
            'sensitivity_analysis',
            # Items 15-17 (to be implemented later)
            'monthly_cashflow',
            'revenue_forecast',
            'cost_forecast',
            # Legacy fields (kept for backward compatibility)
            'project_description_text',
            'project_description_table',
            'timeline_dates',
            'sales_timeline',
            'break_even',
            'index_values',
            'cashflow',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DataInputUpdateSerializer(serializers.Serializer):
    """Serializer for updating individual data input fields"""
    data = serializers.JSONField()

    def validate_data(self, value):
        """Basic validation for JSON data"""
        if not isinstance(value, (dict, list)):
            raise serializers.ValidationError("Data must be a valid JSON object or array")
        return value


class ConstructionProgressSerializer(serializers.ModelSerializer):
    """Serializer for ConstructionProgress model"""
    project_id = serializers.CharField(source='project.project_id', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = ConstructionProgress
        fields = [
            'id',
            'project',
            'project_id',
            'project_name',
            'total_contract_amount',
            'available_floors',
            'tasks',
            'overall_completion_percentage',
            'total_spent_to_date',
            'original_file_name',
            'uploaded_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ConstructionProgressSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for ConstructionProgressSnapshot model"""
    project_id = serializers.CharField(source='project.project_id', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = ConstructionProgressSnapshot
        fields = [
            'id',
            'project',
            'project_id',
            'project_name',
            'snapshot_date',
            'month',
            'year',
            'tasks_snapshot',
            'overall_completion_percentage',
            'total_spent',
            'notes',
            'created_by',
            'created_at'
        ]
        read_only_fields = ['created_at']


class ConstructionProgressUploadSerializer(serializers.Serializer):
    """Serializer for uploading construction progress (Excel file or pasted data)"""
    file = serializers.FileField(required=False, help_text="Excel file to upload")
    pasted_data = serializers.JSONField(required=False, help_text="Pasted data from Excel")
    original_file_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """Ensure either file or pasted_data is provided"""
        if not data.get('file') and not data.get('pasted_data'):
            raise serializers.ValidationError(
                "Either 'file' or 'pasted_data' must be provided"
            )
        if data.get('file') and data.get('pasted_data'):
            raise serializers.ValidationError(
                "Provide either 'file' or 'pasted_data', not both"
            )
        return data


class ConstructionProgressUpdateSerializer(serializers.Serializer):
    """Serializer for updating construction progress task values"""
    tasks = serializers.ListField(
        child=serializers.DictField(),
        help_text="Updated tasks array with floor progress values"
    )
    available_floors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Updated list of available floors (if floor structure changed)"
    )

    def validate_tasks(self, value):
        """Validate tasks structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Tasks must be a list")

        for task in value:
            if not isinstance(task, dict):
                raise serializers.ValidationError("Each task must be a dictionary")

            # Validate required fields
            required_fields = ['task_number', 'chapter', 'work_item', 'floor_progress']
            for field in required_fields:
                if field not in task:
                    raise serializers.ValidationError(
                        f"Task missing required field: {field}"
                    )

        return value


class BankTransactionSerializer(serializers.ModelSerializer):
    """Serializer for BankTransaction model"""
    project_id = serializers.CharField(source='project.project_id', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    bank_display = serializers.CharField(source='get_bank_display', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = BankTransaction
        fields = [
            'id',
            'project',
            'project_id',
            'project_name',
            'bank',
            'bank_display',
            'account_number',
            'transaction_date',
            'value_date',
            'description',
            'reference_number',
            'transaction_type',
            'transaction_type_display',
            'amount',
            'balance',
            'status',
            'status_display',
            'approval_notes',
            'approved_by',
            'approved_date',
            'category',
            'category_display',
            'is_construction_related',
            'meets_plan',
            'meets_construction_stage',
            'uploaded_file',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'project': {'required': False},  # Not required on partial updates (PATCH)
        }


class BankStatementUploadSerializer(serializers.Serializer):
    """Serializer for uploading bank statements (Excel files)"""
    file = serializers.FileField(required=True, help_text="Bank statement Excel file")

    def validate_file(self, value):
        """Validate file extension"""
        allowed_extensions = ['.xlsx', '.xls']
        file_name = value.name.lower()
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        return value


class BankTransactionApprovalSerializer(serializers.Serializer):
    """Serializer for approving/rejecting bank transactions"""
    status = serializers.ChoiceField(
        choices=['APPROVED', 'REJECTED'],
        required=True,
        help_text="Approval status"
    )
    approval_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Notes about the approval/rejection"
    )
    approved_by = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Name of person approving"
    )
    category = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Category for the transaction"
    )
    is_construction_related = serializers.BooleanField(
        required=False,
        help_text="Is this transaction related to construction?"
    )


class BankTransactionBulkApprovalSerializer(serializers.Serializer):
    """Serializer for bulk approval/rejection"""
    transaction_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of transaction IDs to approve/reject"
    )
    status = serializers.ChoiceField(
        choices=['APPROVED', 'REJECTED'],
        required=True
    )
    approval_notes = serializers.CharField(required=False, allow_blank=True)
    approved_by = serializers.CharField(required=False, allow_blank=True)


class EquityDepositSerializer(serializers.ModelSerializer):
    """Serializer for EquityDeposit model"""
    project_id = serializers.CharField(source='project.project_id', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    # Make optional fields explicitly not required
    bank_transaction = serializers.PrimaryKeyRelatedField(
        queryset=BankTransaction.objects.all(),
        required=False,
        allow_null=True
    )
    created_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reference_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = EquityDeposit
        fields = [
            'id',
            'project',
            'project_id',
            'project_name',
            'deposit_date',
            'amount',
            'source',
            'source_display',
            'description',
            'reference_number',
            'notes',
            'bank_transaction',
            'created_by',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProjectDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ProjectDocument model"""
    project_id = serializers.CharField(source='project.project_id', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectDocument
        fields = [
            'id',
            'project',
            'project_id',
            'project_name',
            'name',
            'description',
            'category',
            'category_display',
            'file',
            'file_url',
            'file_name',
            'file_size',
            'file_type',
            'document_date',
            'tags',
            'uploaded_by',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['file_name', 'file_size', 'file_type', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ProjectDocumentUploadSerializer(serializers.Serializer):
    """Serializer for uploading project documents"""
    file = serializers.FileField(required=True, help_text="Document file to upload")
    name = serializers.CharField(required=True, help_text="Document name")
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.ChoiceField(
        choices=ProjectDocument.CATEGORY_CHOICES,
        default='OTHER'
    )
    document_date = serializers.DateField(required=False, allow_null=True)
    tags = serializers.JSONField(required=False, default=list)

    def validate_file(self, value):
        """Validate file size and type"""
        max_size = 50 * 1024 * 1024  # 50 MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed ({max_size // (1024*1024)} MB)"
            )
        return value
