from .base import *  # noqa: F403

from django.core.exceptions import ImproperlyConfigured


DEBUG = False
if not os.getenv("DJANGO_SECRET_KEY") and not os.getenv("SECRET_KEY"):  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be configured in production.")
if SECRET_KEY == "dev-only-change-me":  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must not use the development fallback in production.")
if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be configured in production.")

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)  # noqa: F405
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)  # noqa: F405
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)  # noqa: F405
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)  # noqa: F405
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)  # noqa: F405
STORAGES = {  # noqa: F405
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
