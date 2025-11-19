"""
Django settings for studentacc project.
"""

from pathlib import Path
import os
import boto3
import json
import sys

# Allow local library import
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.join(BASE_DIR, 'studentaccommodationlib', 'src'))

# ============================================================
# 🔐 1. Load Secrets From AWS Secrets Manager
# ============================================================
def get_secret(secret_name):
    """Load JSON secret from AWS Secrets Manager (safe fallback)."""
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        print("✅ Loaded secrets from AWS Secrets Manager")
        return json.loads(response["SecretString"])
    except Exception as e:
        print("❌ Could not load secret:", e)
        return {}   # fallback (local dev mode)


# Load secrets
secrets = get_secret("student-accommodation-secrets")


# ============================================================
# 🔑 2. Security / Base Config
# ============================================================
SECRET_KEY = secrets.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-k0_^ahy01jr9o5y5+!$7-_svf^+s4av9vmw(^*=1j#dk9seqr9"
)

DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.vfs.cloud9.us-east-1.amazonaws.com",
]


# ============================================================
# 📦 3. Applications
# ============================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your app
    "accommodation.apps.AccommodationConfig",

    # S3 media storage
    "storages",
]


# ============================================================
# 🔧 4. Middleware
# ============================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "accommodation.middleware.DisableClientCacheMiddleware",  # last
]


# ============================================================
# 🌐 5. URL/WSGI
# ============================================================
ROOT_URLCONF = "studentacc.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "studentacc.wsgi.application"


# ============================================================
# 🗄️ 6. Database
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ============================================================
# 🔐 7. Password Validation
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================================================
# 🌍 8. Internationalization
# ============================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ============================================================
# 📁 9. Static & Media (S3) Settings
# ============================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Your new S3 bucket in this lab
AWS_S3_REGION_NAME = "us-east-1"
AWS_STORAGE_BUCKET_NAME = secrets.get(
    "AWS_S3_BUCKET",
    "studentaccommodation-media-harish-new-lab"
)

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"


# ============================================================
# 👤 10. Login/Logout
# ============================================================
LOGIN_REDIRECT_URL = "accommodation:accommodation_list"
LOGOUT_REDIRECT_URL = "login"
LOGIN_URL = "login"


# ============================================================
# 📧 11. Email Backend
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ============================================================
# 🧁 12. Sessions
# ============================================================
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 600     # 10 minutes
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

SESSION_FILE_PATH = "/tmp/django_sessions"

CACHE_MIDDLEWARE_SECONDS = 0
CACHE_MIDDLEWARE_KEY_PREFIX = ""


# ============================================================
# 🎉 ALL SET
# ============================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
