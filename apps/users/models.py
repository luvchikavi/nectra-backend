from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role-based access control"""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    email = models.EmailField(unique=True, blank=False, null=False)

    # Expanded role choices for construction project management
    USER_ROLES = [
        ('SUPER_ADMIN', 'מנהל מערכת / Super Admin'),
        ('COMPANY_ADMIN', 'מנהל חברה / Company Admin'),
        ('PROJECT_MANAGER', 'מנהל פרויקט / Project Manager'),
        ('ACCOUNTANT', 'חשב / Accountant'),
        ('FIELD_SUPERVISOR', 'מפקח שטח / Field Supervisor'),
        ('CONTRACTOR', 'קבלן משנה / Contractor'),
        ('VIEWER', 'צופה / Viewer'),
        ('BANK_LIAISON', 'נציג בנק / Bank Liaison'),
    ]

    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default='VIEWER',
        verbose_name="תפקיד / Role"
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="טלפון / Phone Number"
    )

    # Company/Organization for multi-tenant support
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="חברה / Company"
    )

    # Projects this user has access to (for non-admin users)
    assigned_projects = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='assigned_users',
        verbose_name="פרויקטים משויכים / Assigned Projects"
    )

    class Meta:
        verbose_name = "משתמש / User"
        verbose_name_plural = "משתמשים / Users"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ==========================================
    # Role check methods
    # ==========================================

    def is_super_admin(self):
        return self.role == 'SUPER_ADMIN' or self.is_superuser

    def is_company_admin(self):
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN'] or self.is_superuser

    def is_project_manager(self):
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER']

    def is_accountant(self):
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER', 'ACCOUNTANT']

    def is_field_supervisor(self):
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER', 'FIELD_SUPERVISOR']

    def is_contractor(self):
        return self.role == 'CONTRACTOR'

    def is_viewer(self):
        return self.role == 'VIEWER'

    def is_bank_liaison(self):
        return self.role == 'BANK_LIAISON'

    # ==========================================
    # Permission check methods
    # ==========================================

    def can_manage_users(self):
        """Can create/edit/delete users"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN'] or self.is_superuser

    def can_create_projects(self):
        """Can create new projects"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN'] or self.is_superuser

    def can_delete_projects(self):
        """Can delete projects"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN'] or self.is_superuser

    def can_view_all_projects(self):
        """Can view all projects (regardless of assignment)"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN'] or self.is_superuser

    def can_edit_project_data(self):
        """Can edit project configuration and data inputs"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER']

    def can_manage_bank_transactions(self):
        """Can view and manage bank transactions"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER', 'ACCOUNTANT']

    def can_approve_transactions(self):
        """Can approve/reject bank transactions"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER']

    def can_update_construction_progress(self):
        """Can update construction progress data"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER', 'FIELD_SUPERVISOR']

    def can_upload_documents(self):
        """Can upload documents"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER', 'ACCOUNTANT', 'FIELD_SUPERVISOR', 'CONTRACTOR']

    def can_view_reports(self):
        """Can view reports and dashboards"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER', 'ACCOUNTANT', 'FIELD_SUPERVISOR', 'VIEWER', 'BANK_LIAISON']

    def can_manage_billing(self):
        """Can manage subscription and billing"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN'] or self.is_superuser

    def can_view_bank_data(self):
        """Can view bank-related data (for bank representatives)"""
        return self.role in ['SUPER_ADMIN', 'COMPANY_ADMIN', 'PROJECT_MANAGER', 'ACCOUNTANT', 'BANK_LIAISON']

    # ==========================================
    # Project access methods
    # ==========================================

    def get_accessible_projects(self):
        """Get all projects this user can access"""
        from apps.projects.models import Project

        if self.can_view_all_projects():
            # Admins see all projects in their company
            if self.company:
                return Project.objects.filter(company=self.company, is_active=True)
            return Project.objects.filter(is_active=True)
        else:
            # Other users see only assigned projects
            return self.assigned_projects.filter(is_active=True)

    def has_project_access(self, project):
        """Check if user has access to a specific project"""
        if self.can_view_all_projects():
            if self.company:
                return project.company == self.company
            return True
        return self.assigned_projects.filter(pk=project.pk).exists()


class Company(models.Model):
    """Company/Organization for multi-tenant support"""

    name = models.CharField(
        max_length=200,
        verbose_name="שם חברה / Company Name"
    )

    # Contact info
    email = models.EmailField(
        blank=True,
        verbose_name="אימייל / Email"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="טלפון / Phone"
    )
    address = models.TextField(
        blank=True,
        verbose_name="כתובת / Address"
    )

    # Business info
    business_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="ח.פ. / Business Number"
    )

    # Subscription info
    SUBSCRIPTION_PLANS = [
        ('TRIAL', 'ניסיון / Trial'),
        ('STARTER', 'סטארטר / Starter'),
        ('PROFESSIONAL', 'מקצועי / Professional'),
        ('ENTERPRISE', 'ארגוני / Enterprise'),
    ]

    subscription_plan = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_PLANS,
        default='TRIAL',
        verbose_name="תכנית / Subscription Plan"
    )

    subscription_expires = models.DateField(
        null=True,
        blank=True,
        verbose_name="תאריך תפוגה / Subscription Expires"
    )

    max_projects = models.IntegerField(
        default=2,
        verbose_name="מקסימום פרויקטים / Max Projects"
    )

    max_users = models.IntegerField(
        default=5,
        verbose_name="מקסימום משתמשים / Max Users"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name="פעיל / Active"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name = 'חברה / Company'
        verbose_name_plural = 'חברות / Companies'

    def __str__(self):
        return self.name

    def get_active_projects_count(self):
        """Get count of active projects"""
        return self.projects.filter(is_active=True).count()

    def get_users_count(self):
        """Get count of users"""
        return self.users.count()

    def can_create_project(self):
        """Check if company can create more projects"""
        return self.get_active_projects_count() < self.max_projects

    def can_add_user(self):
        """Check if company can add more users"""
        return self.get_users_count() < self.max_users


class UserSettings(models.Model):
    """User settings and preferences"""

    LANGUAGE_CHOICES = [
        ('he', 'עברית'),
        ('en', 'English'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name="משתמש / User"
    )

    # Company settings (for admin users)
    company_name = models.CharField(
        max_length=100,
        default='Nectra',
        verbose_name="שם חברה / Company Name"
    )

    # Display preferences
    dark_mode = models.BooleanField(
        default=False,
        verbose_name="מצב כהה / Dark Mode"
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='he',
        verbose_name="שפה / Language"
    )

    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="התראות במייל / Email Notifications"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_settings'
        verbose_name = 'הגדרות משתמש / User Settings'
        verbose_name_plural = 'הגדרות משתמשים / User Settings'

    def __str__(self):
        return f"Settings for {self.user.username}"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create settings for a user"""
        settings, created = cls.objects.get_or_create(user=user)
        return settings
