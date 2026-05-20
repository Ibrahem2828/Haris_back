from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.incidents.serializers import AlertSerializer
from apps.logs.serializers import ActivityLogSerializer

from .services.metrics import DashboardMetrics


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["dashboard"],
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Dashboard summary",
                value={"devices_count": 10, "vlans_count": 4, "logs_count": 1500, "alerts_count": 25, "critical_alerts": 2, "high_alerts": 8, "last_attack": "Port Scan", "most_suspicious_ip": "192.168.20.15", "system_status": "warning"},
                response_only=True,
            )
        ],
    )
    def get(self, request):
        return Response(DashboardMetrics().summary())


class RecentAlertsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=AlertSerializer(many=True))
    def get(self, request):
        alerts = DashboardMetrics().recent_alerts()
        return Response(AlertSerializer(alerts, many=True).data)


class RecentLogsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=ActivityLogSerializer(many=True))
    def get(self, request):
        logs = DashboardMetrics().recent_logs()
        return Response(ActivityLogSerializer(logs, many=True).data)


class AttackDistributionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().attack_distribution())


class TopSuspiciousIPsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().top_suspicious_ips())


class NetworkMapView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().network_map())


class SecurityPostureView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().security_posture())


class AlertsTimeseriesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().alerts_timeseries(request.query_params.get("range", "24h")))


class SeverityBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().severity_breakdown())


class VLANRiskView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().vlan_risk())


class DeviceRiskView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().device_risk())


class DetectionHealthView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().detection_health())


class IncidentStatusBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().incident_status_breakdown())


class ResponseStatusBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["dashboard"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response(DashboardMetrics().response_status_breakdown())
