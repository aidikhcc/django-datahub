import os
from pathlib import Path
from .azure_ad_settings import AZURE_AD

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

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
        'level': 'DEBUG',
    },
}

ALLOWED_HOSTS = [
    'khcc-datahub.azurewebsites.net',
    'localhost',
    '127.0.0.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'kpi_tracker.apps.KpiTrackerConfig',
    'event_reporting',
    'registries.apps.RegistriesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cancer_center.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'registries', 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'cancer_center.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'AIDI-DB',
        'HOST': 'aidi-db-server.database.windows.net',
        'PORT': '1433',
        'USER': 'aidiadmin',
        'PASSWORD': 'KhCc@2024!',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'MARS_Connection': 'True',
            'ENCRYPT': 'yes',
            'TRUST_SERVER_CERTIFICATE': 'no',
            'CONNECTION_TIMEOUT': 30,
            'driver_supports_utf8': True,
            'unicode_results': True,
        },
    }
}

# Add database options for schema
DATABASE_OPTIONS = {
    'default': {
        'OPTIONS': {
            'use_schema': True,
            'schema': 'datahub'
        }
    }
}

# Add Azure Key Vault settings
AZURE_KEY_VAULT_URL = "https://aidi-keyvault.vault.azure.net/"
AZURE_KEY_VAULT_SECRET_NAME = "SqlDbPassword"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Use a simpler static files storage that doesn't require a manifest
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# WhiteNoise Configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True

# Make sure the directory structure exists
os.makedirs(os.path.join(BASE_DIR, "static", "images"), exist_ok=True)

# Make sure WhiteNoiseMiddleware is in the correct order
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Right after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URL for @login_required decorator
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = AZURE_AD['LOGOUT_URI']

# Add this after DATABASES configuration
DATABASE_ROUTERS = ['kpi_tracker.db_router.AzureDBRouter']

AUTHENTICATION_BACKENDS = [
    'kpi_tracker.auth_backends.AzureADBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Azure AD Settings
AZURE_AD_AUTH = {
    'TENANT_ID': AZURE_AD['TENANT_ID'],
    'CLIENT_ID': AZURE_AD['CLIENT_ID'],
    'CLIENT_SECRET': AZURE_AD['CLIENT_SECRET'],
    'REDIRECT_URI': AZURE_AD['REDIRECT_URI'],
    'AUTHORITY': AZURE_AD['AUTHORITY'],
    'SCOPE': AZURE_AD['SCOPE'],
    'RESPONSE_TYPE': AZURE_AD['RESPONSE_TYPE'],
    'RESPONSE_MODE': AZURE_AD['RESPONSE_MODE'],
}

# Add SITE_ID
SITE_ID = 1

# Update Auth settings
AUTH_USER_MODEL = 'kpi_tracker.User'

# Security settings for production - Modified to fix redirect loop
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
