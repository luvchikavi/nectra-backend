"""
Local development settings
- Easy to use without complex setup
- SQLite database (no PostgreSQL needed)
- AllowAny permissions (no auth required for testing)
- CORS allows all origins
"""
from .base import *

# Development SECRET_KEY - only for local development!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key-do-not-use-in-production')

# Debug mode for development
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Use SQLite for local development/testing (no PostgreSQL needed)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Celery in eager mode for testing (runs synchronously)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ============================================
# DEVELOPMENT-ONLY SETTINGS (DO NOT USE IN PRODUCTION)
# ============================================

# CORS - Allow all origins for easy frontend development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework - AllowAny for easy API testing during development
# In production, this is overridden to require authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # DEV ONLY - production requires auth
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# Logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
