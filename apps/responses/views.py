from django.utils import timezone
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import decorators, response, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.audit.services import audit_log
from apps.common.permissions import CanApproveResponse
from apps.incidents.services.workflow import IncidentWorkflow

from .models import ResponseAction
from .serializers import (
    ResponseActionSerializer,
    ResponseExecutedSerializer,
    ResponsePreviewSerializer,
    ResponseRejectSerializer,
)


class ResponseActionFilter(filters.FilterSet):
    created_at_after = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = ResponseAction
        fields = ["action_type", "risk_level", "approval_status", "requires_approval", "executed"]


class ResponseActionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResponseAction.objects.select_related("alert", "approved_by").all()
    serializer_class = ResponseActionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ResponseActionFilter
    ordering_fields = ["created_at", "updated_at", "risk_level", "approval_status"]
    search_fields = ["title", "description", "recommended_action", "alert__source_ip"]

    @extend_schema(
        tags=["responses"],
        description="Approve a pending response action. Requires ADMIN or NETWORK_ADMIN role.",
        examples=[
            OpenApiExample(
                "Approved response",
                value={"id": 1, "approval_status": "approved", "executed": False},
                response_only=True,
            )
        ],
    )
    @decorators.action(detail=True, methods=["post"], permission_classes=[CanApproveResponse])
    def approve(self, request, pk=None):
        action = self.get_object()
        action.approval_status = ResponseAction.ApprovalStatuses.APPROVED
        action.approved_by = request.user
        action.approved_at = timezone.now()
        action.save(update_fields=["approval_status", "approved_by", "approved_at", "updated_at"])
        IncidentWorkflow().approve(action.alert, request.user)
        audit_log(request.user, "response_approved", "ResponseAction", action.id, request)
        return response.Response(ResponseActionSerializer(action).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[CanApproveResponse])
    def reject(self, request, pk=None):
        action = self.get_object()
        serializer = ResponseRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data.get("reason", "")
        action.approval_status = ResponseAction.ApprovalStatuses.REJECTED
        action.rejected_reason = reason
        action.save(update_fields=["approval_status", "rejected_reason", "updated_at"])
        IncidentWorkflow().reject(action.alert, request.user, reason)
        audit_log(request.user, "response_rejected", "ResponseAction", action.id, request, {"reason": reason})
        return response.Response(ResponseActionSerializer(action).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[CanApproveResponse])
    def postpone(self, request, pk=None):
        action = self.get_object()
        action.approval_status = ResponseAction.ApprovalStatuses.POSTPONED
        action.save(update_fields=["approval_status", "updated_at"])
        audit_log(request.user, "response_postponed", "ResponseAction", action.id, request)
        return response.Response(ResponseActionSerializer(action).data)

    @decorators.action(detail=True, methods=["post"], url_path="mark-executed", permission_classes=[CanApproveResponse])
    def mark_executed(self, request, pk=None):
        action = self.get_object()
        serializer = ResponseExecutedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action.executed = True
        action.executed_at = timezone.now()
        action.execution_notes = serializer.validated_data.get("execution_notes", "")
        action.save(update_fields=["executed", "executed_at", "execution_notes", "updated_at"])
        IncidentWorkflow().record_timeline(action.alert, "executed", request.user, "Response marked executed.")
        audit_log(request.user, "response_executed", "ResponseAction", action.id, request)
        return response.Response(ResponseActionSerializer(action).data)


class GeneratePreviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["responses"],
        request=ResponsePreviewSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Port scan preview",
                value={"attack_type": "port_scan", "source_ip": "192.168.20.15", "destination_ip": "192.168.30.10", "evidence": {}},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = ResponsePreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.create_preview(), status=status.HTTP_200_OK)
