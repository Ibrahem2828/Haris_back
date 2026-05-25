from django.contrib import admin
from django.urls import include, path
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["health"],
        auth=[],
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Healthy service",
                value={"status": "ok", "database": "ok", "redis": "not_configured", "version": "1.0.0"},
                response_only=True,
            )
        ],
    )
    def get(self, request):
        from django.conf import settings
        from django.db import connection

        database = "ok"
        response_status = status.HTTP_200_OK
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            database = "error"
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE

        redis_status = "not_configured"
        if getattr(settings, "REDIS_URL", ""):
            try:
                import redis

                redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1).ping()
                redis_status = "ok"
            except Exception:
                redis_status = "error"

        service_status = "ok" if database == "ok" else "error"
        return Response(
            {"status": service_status, "database": database, "redis": redis_status, "version": settings.HARIS_VERSION},
            status=response_status,
        )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/logs/", include("apps.logs.urls")),
    path("api/detection/", include("apps.detection.urls")),
    path("api/incidents/", include("apps.incidents.urls")),
    path("api/responses/", include("apps.responses.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/simulator/", include("apps.simulator.urls")),
    path("api/arp/", include("apps.arp.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/audit/", include("apps.audit.urls")),
    path("health/", HealthView.as_view(), name="root-health"),
    path("api/health/", HealthView.as_view(), name="health"),
]
