"""
Django settings for techsense project.
Local development version (no deployment extras).
"""

from pathlib import Path
import os
import dj_database_url
#from django.conf import settings  # already imported at top? then skip this

# ----------------------------------------------------
# Paths
# ----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------
# Basic security / debug
# ----------------------------------------------------
SECRET_KEY = 'django-insecure-6i+_lksx=4j6a4tpxo*kl^ad_2e**axw&7%%q&u^(lrnr9niv6'

# Local development only – keep True
DEBUG = os.getenv("DEBUG", "True") == "True"

# ---------- Security for Railway (HTTPS behind proxy) ----------
if not DEBUG:
    # Tell Django that the proxy sets X-Forwarded-Proto to 'https'
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Cookies should only be sent over HTTPS in production
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True


# ALLOWED_HOSTS: list[str] = []
# ALLOWED_HOSTS = ["*", ".railway.app", "127.0.0.1", "localhost"]
ALLOWED_HOSTS = [
    "web-production-78712.up.railway.app",  # your exact Railway URL
    ".up.railway.app",                      # any other Railway subdomain
    "127.0.0.1",
    "localhost",
]
CSRF_TRUSTED_ORIGINS = [
    "https://web-production-78712.up.railway.app",
    "https://*.up.railway.app",
]

LOGIN_URL = 'store:login'

# ----------------------------------------------------
# Installed apps
# ----------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'store',
    # if you later install django-widget-tweaks, you can add:
    # 'widget_tweaks',
]

# ----------------------------------------------------
# Middleware
# ----------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'techsense.urls'

# ----------------------------------------------------
# Templates
# ----------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # project-level templates folder (where base.html is)
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

WSGI_APPLICATION = 'techsense.wsgi.application'

# ----------------------------------------------------
# Database – SQLite for local dev
# ----------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )


# ----------------------------------------------------
# Password validation
# ----------------------------------------------------
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

# ----------------------------------------------------
# Internationalization
# ----------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'   # you can change if you want
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------
# Static & media files
# ----------------------------------------------------
STATIC_URL = '/static/'

# where Django will collect static files if you run collectstatic
STATIC_ROOT = BASE_DIR / 'staticfiles'

# extra static folders used in development
STATICFILES_DIRS = [
    BASE_DIR / 'static',                # optional project-level static/
    BASE_DIR / 'store' / 'static',      # your existing store/static
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ----------------------------------------------------
# Default primary key field type
# ----------------------------------------------------
# For local development: print emails to console instead of sending


# ---------------- EMAIL SETTINGS ----------------
# ---------------- EMAIL SETTINGS ----------------
if DEBUG:
    # Local dev: just print emails in console
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    # Production: real SMTP (Gmail)
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")         # your Gmail address
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD") # your Gmail app password
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
