# File: clubhouse/settings.py
from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# Use an environment variable for the Django secret key; falls back to a dev-only placeholder
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-me')
DEBUG = True


# Host & CSRF config for LAN dev
ALLOWED_HOSTS = ['*'] if DEBUG else ['127.0.0.1', 'localhost', '10.0.0.92']
CSRF_TRUSTED_ORIGINS = ['http://10.0.0.92:8000']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'accounts',
    'elections',
    'tasksapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'clubhouse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'clubhouse.wsgi.application'

# SQLite (good for LAN)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'tasksapp:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

# File upload limits (avatars up to 2 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024

FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024

# --- Defensive defaults for LAN dev ---
# If other imports or overrides cleared these, set safe dev defaults.
try:
    ALLOWED_HOSTS
except NameError:
    ALLOWED_HOSTS = []

if not ALLOWED_HOSTS:
    # In DEBUG, accept all hosts for convenience on LAN; otherwise allow localhost + LAN IP.
    ALLOWED_HOSTS = ['*'] if DEBUG else ['127.0.0.1', 'localhost', '10.0.0.92']

# Ensure CSRF trusted origins is set for IP access with port 8000
if 'CSRF_TRUSTED_ORIGINS' not in globals() or not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        'http://10.0.0.92:8000',
    ]
