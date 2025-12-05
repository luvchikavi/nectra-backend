from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'role_display',
        'is_staff',
        'is_active'
    ]
    list_filter = BaseUserAdmin.list_filter + ('role',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Appraisal Office Settings', {
            'fields': ('role', 'phone_number')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Appraisal Office Settings', {
            'fields': ('role', 'phone_number')
        }),
    )
    
    def role_display(self, obj):
        colors = {
            'APPRAISER': '#2196F3',
            'TEAM_MANAGER': '#FF9800',
            'OFFICE_MANAGER': '#4CAF50'
        }
        color = colors.get(obj.role, '#000000')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_display.short_description = 'Role'
