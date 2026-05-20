from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import decorators, response, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Alert
from .serializers import AlertNoteSerializer, AlertReasonSerializer, AlertSerializer, AlertStatusSerializer, AlertTimelineSerializer
from .services.workflow import IncidentWorkflow


class AlertFilter(filters.FilterSet):
    created_at_after = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Alert
        fields = ["attack_type", "severity", "status", "source_ip", "destination_ip"]


@extend_schema_view(
    retrieve=extend_schema(
        tags=["incidents"],
        examples=[
            OpenApiExample(
                "Alert detail",
                value={
                    "id": 1,
                    "attack_type": "port_scan",
                    "source_ip": "192.168.20.15",
                    "destination_ip": "192.168.30.10",
                    "severity": "high",
                    "status": "new",
                    "description": "Multiple ports contacted in a short time window.",
                },
                response_only=True,
            )
        ],
    )
)
class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects.select_related("rule").all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AlertFilter
    search_fields = ["attack_type", "source_ip", "destination_ip", "description"]
    ordering_fields = ["created_at", "first_seen", "last_seen", "severity", "status"]

    @decorators.action(detail=True, methods=["patch"], url_path="status")
    def set_status(self, request, pk=None):
        alert = self.get_object()
        serializer = AlertStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        alert = IncidentWorkflow().transition(
            alert,
            serializer.validated_data["status"],
            request.user,
            serializer.validated_data.get("notes") or "Status updated from legacy endpoint.",
            "status_changed",
            allow_any_non_closed=True,
        )
        return response.Response(AlertSerializer(alert).data)

    @decorators.action(detail=True, methods=["post"], url_path="mark-false-positive")
    def mark_false_positive(self, request, pk=None):
        alert = self.get_object()
        serializer = AlertReasonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        alert = IncidentWorkflow().mark_false_positive(alert, request.user, serializer.validated_data.get("notes"))
        return response.Response(AlertSerializer(alert).data)

    @decorators.action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        alert = self.get_object()
        serializer = AlertReasonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        alert = IncidentWorkflow().close(alert, request.user, serializer.validated_data.get("notes"))
        return response.Response(AlertSerializer(alert).data)

    @decorators.action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        alert = self.get_object()
        return response.Response(AlertTimelineSerializer(alert.timeline.select_related("actor"), many=True).data)

    @decorators.action(detail=True, methods=["post"], url_path="start-review")
    def start_review(self, request, pk=None):
        alert = IncidentWorkflow().start_review(self.get_object(), request.user)
        return response.Response(AlertSerializer(alert).data)

    @decorators.action(detail=True, methods=["post"], url_path="suggest-response")
    def suggest_response(self, request, pk=None):
        alert = IncidentWorkflow().suggest_response(self.get_object())
        return response.Response(AlertSerializer(alert).data)

    @decorators.action(detail=True, methods=["post"], url_path="mark-resolved")
    def mark_resolved(self, request, pk=None):
        serializer = AlertReasonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        alert = IncidentWorkflow().mark_resolved(self.get_object(), request.user, serializer.validated_data.get("notes"))
        return response.Response(AlertSerializer(alert).data)

    @decorators.action(detail=True, methods=["post"], url_path="add-note")
    def add_note(self, request, pk=None):
        serializer = AlertNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = IncidentWorkflow().add_note(self.get_object(), request.user, serializer.validated_data["message"])
        return response.Response(AlertTimelineSerializer(note).data)
