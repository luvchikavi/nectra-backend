"""
Permission classes for Nectar API
Based on user roles and project assignments
"""

from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """
    Base permission - requires authentication
    In production, all views should use this
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsSuperAdmin(permissions.BasePermission):
    """Only super admins (system-wide access)"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_super_admin()


class IsCompanyAdmin(permissions.BasePermission):
    """Company admins or higher"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_company_admin()


class IsProjectManager(permissions.BasePermission):
    """Project managers or higher"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_project_manager()


class CanManageUsers(permissions.BasePermission):
    """Can manage users (create, edit, delete)"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_manage_users()


class CanCreateProjects(permissions.BasePermission):
    """Can create new projects"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_create_projects()


class CanEditProjectData(permissions.BasePermission):
    """Can edit project data inputs"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_edit_project_data()


class CanManageBankTransactions(permissions.BasePermission):
    """Can view and manage bank transactions"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_manage_bank_transactions()


class CanApproveTransactions(permissions.BasePermission):
    """Can approve/reject bank transactions"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_approve_transactions()


class CanUpdateConstructionProgress(permissions.BasePermission):
    """Can update construction progress"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_update_construction_progress()


class CanUploadDocuments(permissions.BasePermission):
    """Can upload documents"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_upload_documents()


class CanViewReports(permissions.BasePermission):
    """Can view reports and dashboards"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_view_reports()


class HasProjectAccess(permissions.BasePermission):
    """
    Object-level permission to check if user has access to a project
    Use with project-related views
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get the project from the object
        project = None
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, 'pk') and obj._meta.model_name == 'project':
            project = obj

        if not project:
            return True  # No project context, allow

        return request.user.has_project_access(project)


class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    Read-only access for everyone, write access for admins only
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow read for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write requires admin
        return request.user.is_company_admin()


class ProjectBasedPermission(permissions.BasePermission):
    """
    Check permissions based on project access and action type
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # List/retrieve - check if user can view any projects
        if request.method in permissions.SAFE_METHODS:
            return True

        # Create - check if user can create projects
        if request.method == 'POST':
            return request.user.can_create_projects()

        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get project from object
        project = obj if hasattr(obj, 'project_id') else getattr(obj, 'project', None)
        if not project and hasattr(obj, 'pk'):
            project = obj

        # Check project access
        if project and not request.user.has_project_access(project):
            return False

        # Delete requires special permission
        if request.method == 'DELETE':
            return request.user.can_delete_projects()

        # Edit requires project manager or higher
        if request.method in ['PUT', 'PATCH']:
            return request.user.can_edit_project_data()

        return True


# Composite permission classes for common use cases

class ProjectViewerPermission(permissions.BasePermission):
    """Can view project data (any authenticated user with project access)"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        project = getattr(obj, 'project', obj)
        return request.user.has_project_access(project)


class ProjectEditorPermission(permissions.BasePermission):
    """Can view and edit project data"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.can_edit_project_data()


class FinancialDataPermission(permissions.BasePermission):
    """Permission for financial data (bank transactions, equity, etc.)"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.can_view_bank_data()
        return request.user.can_manage_bank_transactions()


class ConstructionDataPermission(permissions.BasePermission):
    """Permission for construction progress data"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view
        return request.user.can_update_construction_progress()
