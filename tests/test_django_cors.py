import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key")
os.environ["CORS_ALLOWED_ORIGINS"] = "http://localhost:3000"
os.environ["CSRF_TRUSTED_ORIGINS"] = "http://localhost:3000"
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver,localhost,127.0.0.1")

import django  # noqa: E402
from django.test import Client  # noqa: E402


django.setup()


def test_login_preflight_allows_localhost_frontend():
    response = Client().options(
        "/api/auth/login/",
        HTTP_ORIGIN="http://localhost:3000",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization,x-csrftoken",
    )

    assert response["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert "POST" in response["Access-Control-Allow-Methods"].upper()
    assert "content-type" in response["Access-Control-Allow-Headers"].lower()
