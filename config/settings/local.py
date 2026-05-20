from .base import *  # noqa: F403


DEBUG = env_bool("DEBUG", True)  # noqa: F405
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", True)  # noqa: F405

if env_bool("USE_SQLITE", True):  # noqa: F405
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.getenv("SQLITE_NAME", BASE_DIR / "db.sqlite3"),  # noqa: F405
        }
    }
