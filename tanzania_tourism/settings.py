

"""
Production-ready Django settings using SQLite (internal SQL file).
Environment-driven via python-decouple (decouple.config).
Ensure you set environment variables in your host environment.
"""

import os
from pathlib import Path
from decouple import config
from django.core.exceptions import ImproperlyConfigured

# -----------------------
# Base / paths
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------
# Basic env-driven flags
# -----------------------
# DEBUG should be False in production by default
DEBUG = config('DEBUG', default=False, cast=bool)

# SECRET_KEY must be set in production
SECRET_KEY = config('SECRET_KEY', default='m9$3kV!q8zP#tR6yWu2nL0sFdG7hB@eXc4vZj^aQp*Yl%Io+1')
if not SECRET_KEY and not DEBUG:
    raise ImproperlyConfigured("SECRET_KEY environment variable is required in production.")

# -----------------------
# Hosts & trusted origins
# -----------------------
def _split_csv(value: str):
    return [s.strip() for s in (value or '').split(',') if s.strip()]

ALLOWED_HOSTS = _split_csv(config('https://tourismproject.pythonanywhere.com'))

# For Django >= 4.0: you should provide scheme://host (example: https://example.com)
CSRF_TRUSTED_ORIGINS = _split_csv(config('CSRF_TRUSTED_ORIGINS', default=''))

# -----------------------
# Apps and middleware
# -----------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_countries',
    'phonenumber_field',
    'corsheaders',
]

LOCAL_APPS = [
    'accounts',
    'parks',
    'tours',
    'bookings',
    'payments',
    'reviews',
    'core',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',    # serve static files in prod
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tanzania_tourism.urls'

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
                'core.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'tanzania_tourism.wsgi.application'

# -----------------------
# Database (SQLite)
# -----------------------
# DB_PATH: absolute path to sqlite file (recommended outside project tree).
DB_PATH = config('DB_PATH', default=str(BASE_DIR / 'db.sqlite3'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
        # reduce "database is locked" by increasing timeout
        'OPTIONS': {
            'timeout': int(config('SQLITE_TIMEOUT', default=20)),
        },
        'TEST': {
            'NAME': str(BASE_DIR / 'test_db.sqlite3'),
        },
    }
}

# -----------------------
# Password validation & auth
# -----------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

AUTH_USER_MODEL = 'accounts.CustomUser'
SITE_ID = config('SITE_ID', default=1, cast=int)

# -----------------------
# Internationalization & timezone
# -----------------------
LANGUAGE_CODE = 'en'
LANGUAGES = [('en', 'English'), ('sw', 'Kiswahili')]
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

# -----------------------
# Static & Media (WhiteNoise)
# -----------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# CompressedManifest is recommended for production cache-busting
STATICFILES_STORAGE = config('STATICFILES_STORAGE', default='whitenoise.storage.CompressedManifestStaticFilesStorage')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------
# Security (only enforced when DEBUG is False)
# -----------------------
# If behind a proxy/load-balancer, set this header at the proxy: X-Forwarded-Proto=https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = int(config('SECURE_HSTS_SECONDS', default=31536000))
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REDIRECT_EXEMPT = []
else:
    SECURE_SSL_REDIRECT = False

# -----------------------
# Email
# -----------------------
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') in ('True', 'true', '1')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'hazinayavitabu@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'ntdq dsqp jwti niks')

if not DEBUG:
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        raise ImproperlyConfigured("EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set in production.")

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=f"{config('SITE_NAME', default='Safari & Bush Retreats')} <{EMAIL_HOST_USER}>")
SITE_URL = config('SITE_URL', default='http://localhost:8000')
SITE_NAME = config('SITE_NAME', default='Safari & Bush Retreats')

# -----------------------
# Django REST Framework
# -----------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(config('PAGE_SIZE', default=20)),
}

# -----------------------
# Celery (optional)
# -----------------------
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# -----------------------
# App-specific / misc keys
# -----------------------
DEFAULT_CURRENCY = config('DEFAULT_CURRENCY', default='USD')
SUPPORTED_CURRENCIES = ['USD', 'EUR', 'TZS', 'KES']

TANZANIA_TOURISM_BOARD_API_KEY = config('TANZANIA_TOURISM_BOARD_API_KEY', default='')
WEATHER_API_KEY = config('WEATHER_API_KEY', default='')

# -----------------------
# Logging (ensure logs dir exists)
# -----------------------
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}', 'style': '{'},
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'tanzania_tourism.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {'handlers': ['console', 'file'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'bookings': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'payments': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
    },
}

# -----------------------
# Final / helpful defaults
# -----------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# CORS (adjust as needed)
CORS_ALLOWED_ORIGINS = _split_csv(config('CORS_ALLOWED_ORIGINS', default=''))
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)

# Informational warning in logs / console when SQLite is used in production
if not DEBUG:
    import logging
    logger = logging.getLogger(__name__)
    if DATABASES['default']['ENGINE'].endswith('sqlite3'):
        logger.warning("Using SQLite in production. Ensure this is intentional: SQLite has concurrency limits.")

# -----------------------
# End of settings
# -----------------------
