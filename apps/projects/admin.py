from django.contrib import admin
from .models import Project, ProjectDataInputs


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'project_name', 'phase', 'created_at', 'updated_at']
    list_filter = ['phase', 'created_at']
    search_fields = ['project_id', 'project_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectDataInputs)
class ProjectDataInputsAdmin(admin.ModelAdmin):
    list_display = ['project', 'created_at', 'updated_at']
    search_fields = ['project__project_name', 'project__project_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Project', {
            'fields': ('project',)
        }),
        ('Property & Description', {
            'fields': ('property_details', 'project_description_text', 'project_description_table')
        }),
        ('Timeline & Sales', {
            'fields': ('timeline_dates', 'sales_timeline')
        }),
        ('Financial Forecasts', {
            'fields': ('revenue_forecast', 'cost_forecast', 'profitability', 'cashflow')
        }),
        ('Analysis', {
            'fields': ('sensitivity_analysis', 'break_even', 'land_value', 'index_values')
        }),
        ('Other', {
            'fields': ('insurance',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
