from django.urls import path, include

urlpatterns = [
    path('users/', include('apps.users.urls')),

    path('sales/', include('apps.sales.urls')),
    path('projects/', include('apps.projects.urls')),
    path('customers/', include('apps.customers.urls')),
    path('budget/', include('apps.budget.urls')),
    path('contractor/', include('apps.contractors.urls')),
    path('reports/', include('apps.reports.urls')),
]
