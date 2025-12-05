from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.v1.urls')),
    path('api/health/', health_check, name='health-check'),
]

# Income-specific URLs (standalone) - TEMPORARILY DISABLED
# from django.urls import path, include
# urlpatterns += [
#     path('api/income/', include('apps.projects.income_urls')),
# ]
