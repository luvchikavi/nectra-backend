"""
Django settings for Nectar project - Railway Deployment

This settings file is optimized for Railway deployment with:
- DATABASE_URL support via dj-database-url
- Simplified logging (console only)
- Optional S3 media storage
"""

from .base import *
import dj_database_url

# ============================================
# CRITICAL SECURITY SETTINGS
# ============================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'temporary-secret-key-change-in-production-123456789')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Railway provides the domain automatically
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.railway.app').split(',')

# ============================================
# HTTPS / SSL SECURITY
# ============================================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ============================================
# CORS - Allow Vercel frontend
# ============================================
CORS_ALLOW_ALL_ORIGINS = True  # Allow all for now - tighten in production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'https://frontendmaterialdashboard-24wduyeuo-avi-luvchiks-projects.vercel.app'
).split(',')

# ============================================
# REST Framework
# ============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# ============================================
# DATABASE - Railway PostgreSQL via DATABASE_URL
# ============================================
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=60,
            ssl_require=True
        )
    }
else:
    # Fallback to SQLite for debugging - NOT for production use
    print("WARNING: DATABASE_URL not set, using SQLite")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',
        }
    }

# ============================================
# STATIC FILES - WhiteNoise
# ============================================
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================
# MEDIA FILES - Local or S3
# ============================================
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
if AWS_ACCESS_KEY_ID:
    # Use S3 if configured
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com' if AWS_STORAGE_BUCKET_NAME else None
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True
else:
    # Use local storage (note: files won't persist across deploys on Railway)
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# ============================================
# LOGGING - Console only for Railway
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================
# CELERY - Disabled for now
# ============================================
CELERY_TASK_ALWAYS_EAGER = True

# ============================================
# SENTRY (Optional)
# ============================================
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
