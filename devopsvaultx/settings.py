"""
Django settings for devopsvaultx project.
Single-file settings (Local + Production handled via DEBUG)
"""

from pathlib import Path
from decouple import config

# ==================================================
# Base
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-test-key-123')

# ==================================================
# BASIC
# ==================================================
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost"
).split(",")

# ==================================================
# CSRF
# ==================================================
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://devopsvaultx.com,https://www.devopsvaultx.com"
).split(",")

# ==================================================
# CORS
# ==================================================
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "https://devopsvaultx.com",
    "https://www.devopsvaultx.com",
]


# ==================================================
# SECURITY CONFIGURATION
# ==================================================
if not DEBUG:
    # Basic Security Headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # SSL & Cookies Logic
    # Redirect to HTTPS only if NOT on localhost/127.0.0.1
    SECURE_SSL_REDIRECT = DEBUG
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS Settings (Strict Transport Security)
    # FIX: Set HSTS to 0 on localhost to avoid "Bad request version" / HTTPS errors
    SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
    SECURE_HSTS_PRELOAD = not DEBUG

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

else:
    # Development / Debug Mode Settings
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0

# ==================================================
# Applications
# ==================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'django_extensions',
    'corsheaders',
    'core',

    # Custom apps
    'accounts',
    'products',
    'dashboard',
    'pages',
    'payments',
    'insights',
    'vaultx',
    'tools',
]

SITE_ID = 1
APPEND_SLASH = True

# ==================================================
# SESSION_COOKIE
# ==================================================
SESSION_COOKIE_AGE = 3600  # 1 hour in seconds
SESSION_SAVE_EVERY_REQUEST = True # User activity session reset

# ==================================================
# Middleware
# ==================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'devopsvaultx.middleware.RequestLoggingMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'devopsvaultx.urls'
WSGI_APPLICATION = 'devopsvaultx.wsgi.application'

# ==================================================
# Templates
# ==================================================
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

# ==================================================
# Database
# ==================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='devopsvaultx_db'),
        'USER': config('POSTGRES_USER', default='admin'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='admin'),
        'HOST': config('POSTGRES_HOST', default='localhost'), # Docker network sathi service name garjeche aahe
        'PORT': config('POSTGRES_PORT', default='5432'),
    }
}
# ==================================================
# Password validation
# ==================================================
AUTH_PASSWORD_VALIDATORS = [
    # १. UserAttributeSimilarityValidator काढला आहे (आता नाव किंवा ईमेल पासवर्डमध्ये वापरता येईल)
    
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,  # तुला हवे असल्यास ६ सुद्धा करू शकतोस
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==================================================
# Internationalization
# ==================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================================================
# Static & Media (Final Corrected Version)
# ==================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Django 5.2/Python 3.14 compatible storage config
if DEBUG:
    # Local Development
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    # Production (Docker/Server)
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
            # 'manifest_strict' kadhun takla aahe TypeError thambvanya sathi.
            # ManifestStaticFilesStorage by default files hash karel.
        },
    }
    
# ==================================================
# Razorpay
# ==================================================
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='rzp_test_S867h1Jsjz4a0u')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='cUuVjTsoVlxbXMohuNEJ9QSN')

# ==================================================
# Email
# ==================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL_SUBJECT = config("CONTACT_EMAIL_SUBJECT")
CONTACT_RECEIVER_EMAIL = config("CONTACT_RECEIVER_EMAIL")

# ==================================================
# Logging
# ==================================================
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "file_info": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "devopsvaultx_json.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "json",
        },
        "file_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "errors_json.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "json",
        },
        # "console": {
        #     "level": "DEBUG",
        #     "class": "logging.StreamHandler",
        #     "formatter": "json",
        # },
    },
    "loggers": {
        "request.audit": {
            "handlers": ["file_info", "file_error"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}