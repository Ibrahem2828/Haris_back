import csv

from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import audit_log
from apps.dashboard.services.metrics import DashboardMetrics
from apps.incidents.models import Alert
from apps.incidents.serializers import AlertSerializer
from apps.logs.models import ActivityLog


class AlertsCSVView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["reports"], responses=OpenApiTypes.BINARY)
    def get(self, request):
        audit_log(request.user, "report_export", "Alert", None, request, {"format": "csv"})
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="haris-alerts.csv"'
        writer = csv.writer(response)
        writer.writerow(["id", "attack_type", "source_ip", "destination_ip", "severity", "status", "first_seen", "last_seen"])
        for alert in Alert.objects.all().order_by("-created_at"):
            writer.writerow([alert.id, alert.attack_type, alert.source_ip, alert.destination_ip, alert.severity, alert.status, alert.first_seen, alert.last_seen])
        return response


class LogsCSVView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["reports"], responses=OpenApiTypes.BINARY)
    def get(self, request):
        audit_log(request.user, "report_export", "ActivityLog", None, request, {"format": "csv"})
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="haris-logs.csv"'
        writer = csv.writer(response)
        writer.writerow(["id", "timestamp", "source_ip", "destination_ip", "protocol", "port", "event_type", "action", "status"])
        for log in ActivityLog.objects.all().order_by("-timestamp"):
            writer.writerow([log.id, log.timestamp, log.source_ip, log.destination_ip, log.protocol, log.port, log.event_type, log.action, log.status])
        return response


class IncidentsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["reports"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        audit_log(request.user, "report_export", "IncidentSummary", None, request, {"format": "json"})
        metrics = DashboardMetrics()
        return Response(
            {
                "summary": metrics.summary(),
                "severity_breakdown": metrics.severity_breakdown(),
                "incident_status_breakdown": metrics.incident_status_breakdown(),
                "response_status_breakdown": metrics.response_status_breakdown(),
            }
        )


class SecurityReportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["reports"], responses=OpenApiTypes.OBJECT)
    def get(self, request):
        audit_log(request.user, "report_export", "SecurityReport", None, request, {"format": "json"})
        metrics = DashboardMetrics()
        top_attacks = list(Alert.objects.values("attack_type").annotate(count=Count("id")).order_by("-count")[:5])
        top_sources = metrics.top_suspicious_ips(5)
        open_incidents = Alert.objects.exclude(status__in=[Alert.Statuses.CLOSED, Alert.Statuses.RESOLVED, Alert.Statuses.FALSE_POSITIVE])[:10]
        return Response(
            {
                "generated_at": timezone.now(),
                "summary": metrics.summary(),
                "top_attacks": top_attacks,
                "top_sources": top_sources,
                "open_incidents": AlertSerializer(open_incidents, many=True).data,
                "recommendations": self._recommendations(),
            }
        )

    def _recommendations(self):
        counts = {row["attack_type"]: row["count"] for row in Alert.objects.values("attack_type").annotate(count=Count("id"))}
        recommendations = []
        if counts.get("port_scan", 0):
            recommendations.append("Review exposed services and validate whether scanned ports should be reachable.")
        if counts.get("vlan_violation", 0):
            recommendations.append("Review inter-VLAN ACLs and segmentation policy.")
        if counts.get("arp_spoofing", 0):
            recommendations.append("Enable switch port security and static ARP bindings where appropriate.")
        if counts.get("icmp_flood", 0):
            recommendations.append("Apply ICMP rate limiting or blocking for abusive sources.")
        if counts.get("ssh_bruteforce", 0):
            recommendations.append("Harden SSH access and block repeated brute force sources.")
        if not recommendations:
            recommendations.append("No attack-specific recommendations are currently required.")
        return recommendations
