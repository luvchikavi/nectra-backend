from rest_framework import serializers
from apps.users.models import User, UserSettings, Company


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['id']


class UserManagementSerializer(serializers.ModelSerializer):
    """Full serializer for user management by admins"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'role_display', 'phone_number', 'is_active',
            'company', 'company_name',
            'date_joined', 'last_login', 'permissions'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'permissions']

    def get_permissions(self, obj):
        return {
            'can_manage_users': obj.can_manage_users(),
            'can_create_projects': obj.can_create_projects(),
            'can_delete_projects': obj.can_delete_projects(),
            'can_view_all_projects': obj.can_view_all_projects(),
            'can_edit_project_data': obj.can_edit_project_data(),
            'can_manage_bank_transactions': obj.can_manage_bank_transactions(),
            'can_approve_transactions': obj.can_approve_transactions(),
            'can_update_construction_progress': obj.can_update_construction_progress(),
            'can_upload_documents': obj.can_upload_documents(),
            'can_view_reports': obj.can_view_reports(),
        }


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'first_name', 'last_name',
            'role', 'phone_number', 'company'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RoleChoicesSerializer(serializers.Serializer):
    """Serializer for role choices"""
    value = serializers.CharField()
    label = serializers.CharField()


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for companies"""
    users_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'business_number',
            'subscription_plan', 'subscription_expires', 'max_projects',
            'max_users', 'is_active', 'users_count', 'projects_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_users_count(self, obj):
        return obj.get_users_count()

    def get_projects_count(self, obj):
        return obj.get_active_projects_count()


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user settings"""

    class Meta:
        model = UserSettings
        fields = [
            'id', 'company_name', 'dark_mode', 'language',
            'email_notifications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
