import logging
import os

from django.apps import AppConfig
from django.conf import settings


logger = logging.getLogger(__name__)


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self):
        if os.environ.get("RUN_MAIN") == "true":
            return
        logger.info(
            "Django startup settings: DJANGO_SETTINGS_MODULE=%s DEBUG=%s ALLOWED_HOSTS=%s "
            "CORS_ALLOWED_ORIGINS=%s CSRF_TRUSTED_ORIGINS=%s",
            os.getenv("DJANGO_SETTINGS_MODULE"),
            settings.DEBUG,
            settings.ALLOWED_HOSTS,
            settings.CORS_ALLOWED_ORIGINS,
            settings.CSRF_TRUSTED_ORIGINS,
        )
