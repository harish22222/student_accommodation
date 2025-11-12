"""
Django settings for studentacc project.
"""

from pathlib import Path
import os
import boto3
import json
import sys

import os

sys.path.append(os.path.join(BASE_DIR, 'studentaccommodationlib', 'src'))

 
# ========================
# FUNCTION TO LOAD SECRETS FROM AWS
# ========================
def get_secret(secret_name):
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        print("✅ Loaded secrets from AWS Secrets Manager")
        return json.loads(secret)
    except Exception as e:
        print("❌ Could not load secret:", e)
        return {}

# ========================
# BASE SETTINGS
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

# Load secrets
secrets = get_secret("student-accommodation-secrets")

SECRET_KEY = secrets.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-k0_^ahy01jr9o5y5+!$7-_svf^+s4av9vmw(^*=1j#dk9seqr9"
)
DEBUG = False

ALLOWED_HOSTS = [
    'student-accommodation-env.eba-im34ivuv.us-east-1.elasticbeanstalk.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://student-accommodation-env.eba-im34ivuv.us-east-1.elasticbeanstalk.com',
    'https://192ef4ce785a40f583434975b96a3cbb.vfs.cloud9.us-east-1.amazonaws.com',
]



# ========================
# APPLICATIONS
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accommodation.apps.AccommodationConfig',
    'storages',
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # ✅ Must be last
    'accommodation.middleware.DisableClientCacheMiddleware',
]

# ========================
# URLS / WSGI
# ========================
ROOT_URLCONF = 'studentacc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'studentacc.wsgi.application'

# ========================
# DATABASE
# ========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ========================
# PASSWORD VALIDATION
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================
# INTERNATIONALIZATION
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========================
# STATIC & MEDIA FILES
# ========================
# 🔹 Static files (for CSS, JS)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 🔹 Media files (for user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================
# LOGIN / LOGOUT SETTINGS
# ========================
LOGIN_REDIRECT_URL = 'accommodation:accommodation_list'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# ========================
# EMAIL BACKEND
# ========================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ========================
# AWS SETTINGS
# ========================
AWS_S3_REGION_NAME = 'us-east-1'
AWS_STORAGE_BUCKET_NAME = secrets.get("AWS_S3_BUCKET", "studentaccommodation-media-harish")
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# ========================
# SESSION CONFIGURATION
# ========================
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 600  # 10 minutes
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

# ✅ Store sessions in temporary files (deleted automatically on restart)
SESSION_FILE_PATH = '/tmp/django_sessions'

# Disable browser caching completely
CACHE_MIDDLEWARE_SECONDS = 0
CACHE_MIDDLEWARE_KEY_PREFIX = ""

WSGI_APPLICATION = 'studentacc.wsgi.application'
