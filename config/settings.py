"""
Django settings for CareBridge-AI project.
Production-ready configuration with PostgreSQL, JWT, Celery, Channels.
"""

import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from decouple import config

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent


def _parse_bool(value):
    """Safely parse DEBUG — handles True/False/1/0/yes/no and ignores non-boolean strings."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ('true', '1', 'yes', 'on')


# Security Settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = _parse_bool(config('DEBUG', default='False'))
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
ENVIRONMENT = config('ENVIRONMENT', default='production')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'daphne',  # Must be first for channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    'django_celery_beat',
    'django_celery_results',
    'phonenumber_field',
    'drf_spectacular',
    'defender',
    
    # CareBridge Apps
    'apps.users',
    'apps.authentication',
    'apps.family',
    'apps.patients',
    'apps.medical_records',
    'apps.companions',
    'apps.services',
    'apps.bookings',
    'apps.care_journey',
    'apps.live_tracking',
    'apps.communication',
    'apps.notifications',
    'apps.payments',
    'apps.reviews',
    'apps.dashboard',
    'apps.analytics',
    'apps.support',
    'apps.document_verification',
    'apps.ai_engine',
    'apps.api_gateway',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.api_gateway.middleware.APIGatewayAuditMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'defender.middleware.FailedLoginMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database Configuration (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='carebridge_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='1407'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    parsed_database = urlparse(DATABASE_URL)
    database_options = {}
    query_options = parse_qs(parsed_database.query)
    if query_options.get('sslmode'):
        database_options['sslmode'] = query_options['sslmode'][0]
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed_database.path.lstrip('/'),
        'USER': unquote(parsed_database.username or ''),
        'PASSWORD': unquote(parsed_database.password or ''),
        'HOST': parsed_database.hostname or '',
        'PORT': parsed_database.port or 5432,
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
        'OPTIONS': database_options,
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Azure Blob Storage configuration
AZURE_STORAGE_ACCOUNT_NAME  = config('AZURE_STORAGE_ACCOUNT_NAME',  default='')
AZURE_STORAGE_ACCOUNT_KEY   = config('AZURE_STORAGE_ACCOUNT_KEY',   default='')
AZURE_STORAGE_CONTAINER_NAME = config('AZURE_STORAGE_CONTAINER_NAME', default='carebridge-media')

# File Storage — Azure in production, local disk in development
if not DEBUG and AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY:
    DEFAULT_FILE_STORAGE  = 'storages.backends.azure_storage.AzureStorage'
    STATICFILES_STORAGE   = 'storages.backends.azure_storage.AzureStorage'
    AZURE_OVERWRITE_FILES = False
    MEDIA_URL = (
        f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/'
        f'{AZURE_STORAGE_CONTAINER_NAME}/'
    )
else:
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.api_gateway.authentication.APIKeyAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=1440, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:5173'
).split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:3000,http://localhost,http://127.0.0.1'
).split(',')


# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Defender Configuration
DEFENDER_REDIS_URL = config('DEFENDER_REDIS_URL', default=CELERY_BROKER_URL)

# Channels Configuration (WebSocket)
REDIS_URL = config('REDIS_URL', default='')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL] if REDIS_URL else [(
                config('REDIS_HOST', default='localhost'),
                config('REDIS_PORT', default=6379, cast=int)
            )],
        },
    },
}

# Email Configuration (SendGrid)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@carebridge.com')
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='support@carebridge.com')
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# Twilio Configuration
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', default='')
FIREBASE_DATABASE_URL = config('FIREBASE_DATABASE_URL', default='')

# Razorpay Configuration
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')
RAZORPAY_WEBHOOK_SECRET = config('RAZORPAY_WEBHOOK_SECRET', default='')

# OpenAI Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4')
OPENAI_MAX_TOKENS = config('OPENAI_MAX_TOKENS', default=2000, cast=int)
OPENAI_TEMPERATURE = config('OPENAI_TEMPERATURE', default=0.7, cast=float)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = config('AZURE_OPENAI_ENDPOINT', default='')
AZURE_OPENAI_API_KEY = config('AZURE_OPENAI_API_KEY', default='')
AZURE_OPENAI_DEPLOYMENT_NAME = config('AZURE_OPENAI_DEPLOYMENT_NAME', default='gpt-4')
AZURE_OPENAI_API_VERSION = config('AZURE_OPENAI_API_VERSION', default='2024-02-15-preview')

# DRF Spectacular (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'CareBridge-AI API',
    'DESCRIPTION': 'AI-powered healthcare companion platform API documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1',
}

# Phone Number Field
PHONENUMBER_DEFAULT_REGION = 'IN'

# Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'carebridge.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'carebridge': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Override channel layer during tests or when Redis is unavailable
import sys

def _redis_available():
    try:
        import redis
        r = redis.Redis(
            host=config('REDIS_HOST', default='localhost'),
            port=config('REDIS_PORT', default=6379, cast=int),
            socket_connect_timeout=1,
        )
        r.ping()
        return True
    except Exception:
        return False

if 'test' in sys.argv or not _redis_available():
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

# CareBridge Business Logic Configuration
COMPANION_SEARCH_RADIUS_KM = config('COMPANION_SEARCH_RADIUS_KM', default=10, cast=int)
MAX_BOOKING_ADVANCE_DAYS = config('MAX_BOOKING_ADVANCE_DAYS', default=30, cast=int)
EMERGENCY_RESPONSE_TIME_MINUTES = config('EMERGENCY_RESPONSE_TIME_MINUTES', default=15, cast=int)
INSTANT_BOOKING_WINDOW_HOURS = config('INSTANT_BOOKING_WINDOW_HOURS', default=4, cast=int)

# Pricing Configuration
BASE_PRICE_PER_HOUR = config('BASE_PRICE_PER_HOUR', default=200, cast=int)
EMERGENCY_SURCHARGE_MULTIPLIER = config('EMERGENCY_SURCHARGE_MULTIPLIER', default=2.0, cast=float)
PLATFORM_COMMISSION_PERCENTAGE = config('PLATFORM_COMMISSION_PERCENTAGE', default=15, cast=int)

# Map Configuration
DEFAULT_LATITUDE = config('DEFAULT_LATITUDE', default=28.7041, cast=float)
DEFAULT_LONGITUDE = config('DEFAULT_LONGITUDE', default=77.1025, cast=float)
DEFAULT_MAP_ZOOM = config('DEFAULT_MAP_ZOOM', default=12, cast=int)

# Sentry Configuration (Production Monitoring)
if not DEBUG and config('SENTRY_DSN', default=''):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=config('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment=ENVIRONMENT,
    )
