"""
Production-ready Django settings using SQLite (internal SQL file).
Environment-driven removed — values are hard-coded per request.
"""

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# -----------------------
# Base / paths
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------
# Basic flags (hard-coded)
# -----------------------
# Set DEBUG to True for local development, False for production
DEBUG = False

# SECRET_KEY (hard-coded — replace with your own long random string)
SECRET_KEY = 'm9$3kV!q8zP#tR6yWu2nL0sFdG7hB@eXc4vZj^aQp*Yl%Io+1'
if not SECRET_KEY and not DEBUG:
    raise ImproperlyConfigured("SECRET_KEY is required in production.")

# -----------------------
# Hosts & trusted origins (hard-coded)
# -----------------------
def _split_csv(value: str):
    return [s.strip() for s in (value or '').split(',') if s.strip()]

ALLOWED_HOSTS = ['tourismproject.pythonanywhere.com', 'localhost', '127.0.0.1']

# For Django >= 4.0: scheme://host entries
CSRF_TRUSTED_ORIGINS = ['https://tourismproject.pythonanywhere.com']

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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
DB_PATH = str(BASE_DIR / 'db.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
        'OPTIONS': {
            'timeout': 20,
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
SITE_ID = 1

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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------
# Security (only enforced when DEBUG is False)
# -----------------------
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REDIRECT_EXEMPT = []
else:
    SECURE_SSL_REDIRECT = False

# -----------------------
# Email (hard-coded — change before production)
# -----------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'hazinayavitabu@gmail.com'
EMAIL_HOST_PASSWORD = 'ntdq dsqp jwti niks'  # <-- Replace with your real password

DEFAULT_FROM_EMAIL = "Safari & Bush Retreats <hazinayavitabu@gmail.com>"
SITE_URL = 'https://tourismproject.pythonanywhere.com'
SITE_NAME = 'Safari & Bush Retreats'

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
    'PAGE_SIZE': 20,
}

# -----------------------
# Celery (hard-coded)
# -----------------------
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# -----------------------
# App-specific / misc keys (hard-coded)
# -----------------------
DEFAULT_CURRENCY = 'USD'
SUPPORTED_CURRENCIES = ['USD', 'EUR', 'TZS', 'KES']

TANZANIA_TOURISM_BOARD_API_KEY = ''
WEATHER_API_KEY = ''

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
CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

# CORS (hard-coded)
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_ALL_ORIGINS = False

# Informational warning in logs / console when SQLite is used in production
if not DEBUG:
    import logging
    logger = logging.getLogger(__name__)
    if DATABASES['default']['ENGINE'].endswith('sqlite3'):
        logger.warning("Using SQLite in production. Ensure this is intentional: SQLite has concurrency limits.")

# -----------------------
# End of settings
# -----------------------
