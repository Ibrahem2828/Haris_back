import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

try:
    from celery import Celery
except ImportError:  # pragma: no cover - lets local checks run before dependencies are installed
    class _MissingCeleryApp:
        def task(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    app = _MissingCeleryApp()
else:
    app = Celery("haris_backend")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
