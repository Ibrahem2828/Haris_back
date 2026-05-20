#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"

if [ -n "$DATABASE_URL" ] || [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for PostgreSQL..."
  python - <<'PY'
import os
import sys
import time
from urllib.parse import urlparse

database_url = os.getenv("DATABASE_URL", "")
if database_url.startswith("sqlite:"):
    sys.exit(0)

timeout = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
deadline = time.monotonic() + timeout
last_error = None

while time.monotonic() < deadline:
    try:
        import django
        from django.db import connection

        django.setup()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("PostgreSQL is ready.")
        sys.exit(0)
    except Exception as exc:
        last_error = exc
        time.sleep(2)

if database_url:
    parsed = urlparse(database_url)
    target = f"{parsed.hostname or 'database'}:{parsed.port or 5432}"
else:
    target = f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', '5432')}"
print(f"PostgreSQL did not become ready at {target}: {last_error}", file=sys.stderr)
sys.exit(1)
PY
fi

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  python manage.py migrate --noinput
fi

if [ "${COLLECTSTATIC:-true}" = "true" ]; then
  python manage.py collectstatic --noinput
fi

if [ "$#" -eq 0 ] || [ "$1" = "gunicorn" ]; then
  exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers "${WEB_CONCURRENCY:-3}" --timeout 120
fi

exec "$@"
