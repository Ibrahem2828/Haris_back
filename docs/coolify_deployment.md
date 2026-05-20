# Haris Backend Coolify Deployment

This guide deploys the Django backend as a Coolify Dockerfile application on port `8000`.

## PostgreSQL Resource

- Create or use the Coolify PostgreSQL resource named `haris-postgres`.
- Use the internal PostgreSQL URL from Coolify inside the backend application.
- Do not point Django at the public PostgreSQL port from inside Coolify.
- SSL is required. Keep `sslmode=require` in `DATABASE_URL` and set `DATABASE_SSL_REQUIRE=True`.
- Use a placeholder in documentation only:

```env
DATABASE_URL=postgres://haris_user:<PASSWORD>@c1zym3o3jlattcd66320io28:5432/postgres?sslmode=require
DATABASE_SSL_REQUIRE=True
```

Never commit or paste the real database password into the repository.

## Backend Application Settings

- Name: `haris-backend`
- Build Pack: `Dockerfile`
- Base Directory: `/`
- Dockerfile Location: `/Dockerfile`
- Exposed Port: `8000`
- Health Check Path: `/api/health/`
- Domain: assign the Coolify-provided backend domain, then add it to `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.

The Dockerfile deployment path is standalone. `docker-compose.yml` and `docker-compose.prod.yml` are reference files only and are not required by Coolify for the backend application.

## Required Environment Variables

```env
DJANGO_ENV=production
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<strong-random-secret>
DJANGO_ALLOWED_HOSTS=api.example.com
DATABASE_URL=postgres://haris_user:<PASSWORD>@c1zym3o3jlattcd66320io28:5432/postgres?sslmode=require
DATABASE_SSL_REQUIRE=True
CORS_ALLOWED_ORIGINS=https://frontend.example.com
CSRF_TRUSTED_ORIGINS=https://frontend.example.com,https://api.example.com
WEB_CONCURRENCY=3
PORT=8000
```

## Optional Environment Variables

```env
REDIS_URL=
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=
SECURE_SSL_REDIRECT=False
HARIS_VERSION=1.0.0
```

Leave Redis and Celery values empty if no Redis resource is configured. The health check reports Redis as `not_configured` and remains healthy when the database is reachable.

## Post-Deploy Commands

Run these from the Coolify application terminal when needed:

```bash
python manage.py createsuperuser
python manage.py seed_detection_rules
python manage.py seed_demo_data
```

The container entrypoint already runs:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

## Troubleshooting

Database connection refused:
Verify the backend uses the internal Coolify PostgreSQL URL, not the public port. Confirm the hostname is `c1zym3o3jlattcd66320io28` and the port is `5432`.

SSL required error:
Keep `?sslmode=require` in `DATABASE_URL` and set `DATABASE_SSL_REQUIRE=True`.

Invalid `ALLOWED_HOSTS`:
Add the exact Coolify backend domain to `DJANGO_ALLOWED_HOSTS`, without protocol. Example: `api.example.com`.

CSRF trusted origin error:
Add HTTPS origins, including protocol, to `CSRF_TRUSTED_ORIGINS`. Example: `https://frontend.example.com,https://api.example.com`.

Static files not loading:
Confirm `collectstatic` completed and the application uses the Dockerfile entrypoint. WhiteNoise serves collected static files from `STATIC_ROOT`.

Health check failed:
Check `/api/health/`. A database error returns HTTP `503`. Redis is optional and should show `not_configured` if empty.

Migrations failed:
Check database credentials, SSL mode, and that the database user can create and modify tables in the selected database.

## Security Notes

- Do not hardcode secrets.
- Configure secrets only through Coolify environment variables.
- Use the internal `DATABASE_URL`.
- Keep PostgreSQL public exposure disabled unless there is a clear operational need.
- Rotate the database password if it has been shared outside the secret manager.
