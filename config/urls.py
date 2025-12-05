from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.v1.urls')),
]

# Income-specific URLs (standalone) - TEMPORARILY DISABLED
# from django.urls import path, include
# urlpatterns += [
#     path('api/income/', include('apps.projects.income_urls')),
# ]
