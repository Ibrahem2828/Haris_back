import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from corsheaders.defaults import default_headers, default_methods


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


DJANGO_ENV = os.getenv("DJANGO_ENV", "local").lower()
IS_PRODUCTION = DJANGO_ENV == "production"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", os.getenv("SECRET_KEY", "dev-only-change-me"))
DEBUG = env_bool("DJANGO_DEBUG", env_bool("DEBUG", False))
DEFAULT_ALLOWED_HOSTS = "" if IS_PRODUCTION else "localhost,127.0.0.1,0.0.0.0"
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", os.getenv("ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "apps.common",
    "apps.accounts",
    "apps.inventory",
    "apps.logs",
    "apps.detection",
    "apps.incidents",
    "apps.responses.apps.ResponsesConfig",
    "apps.dashboard",
    "apps.simulator",
    "apps.arp",
    "apps.reports",
    "apps.audit",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASE_SSL_REQUIRE = env_bool("DATABASE_SSL_REQUIRE", False)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=DATABASE_SSL_REQUIRE,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "haris"),
            "USER": os.getenv("POSTGRES_USER", "haris"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "haris"),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 600,
        }
    }
    if DATABASE_SSL_REQUIRE:
        DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("PAGE_SIZE", "50")),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Haris Cybersecurity Monitoring API",
    "DESCRIPTION": "Production-ready backend APIs for Haris / حارس.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": "auth", "description": "JWT authentication and user profile"},
        {"name": "inventory", "description": "Networks, VLANs, and devices"},
        {"name": "logs", "description": "Activity log ingestion and syslog-like input"},
        {"name": "detection", "description": "Detection rules and jobs"},
        {"name": "incidents", "description": "Alerts and incident workflow"},
        {"name": "responses", "description": "Suggested response actions and approvals"},
        {"name": "dashboard", "description": "Dashboard metrics"},
        {"name": "reports", "description": "Exports and security reports"},
        {"name": "audit", "description": "Audit trail"},
    ],
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "apps.common": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_STARTUP_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

LOCAL_FRONTEND_ORIGINS = (
    "http://localhost:3000,"
    "http://127.0.0.1:3000,"
    "http://localhost:8000,"
    "http://127.0.0.1:8000"
)
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "" if IS_PRODUCTION else LOCAL_FRONTEND_ORIGINS)
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", DEBUG and not CORS_ALLOWED_ORIGINS)
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "" if IS_PRODUCTION else LOCAL_FRONTEND_ORIGINS)
CORS_ALLOW_HEADERS = list(
    dict.fromkeys(
        [
            *default_headers,
            "content-type",
            "authorization",
            "x-csrftoken",
        ]
    )
)
CORS_ALLOW_METHODS = list(
    dict.fromkeys(
        [
            *default_methods,
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ]
    )
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

REDIS_URL = os.getenv("REDIS_URL", "").strip()
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL).strip()
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL).strip()
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", False)
HARIS_VERSION = os.getenv("HARIS_VERSION", "1.0.0")
