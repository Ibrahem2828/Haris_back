from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import audit_log
from apps.common.permissions import IsAdminUserForUnsafe
from apps.common.serializers import EmptySerializer

from .models import ActivityLog
from .serializers import ActivityLogSerializer, BulkActivityLogSerializer
from .services.parser import parse_csv_upload, parse_json_upload, parse_syslog_message


class ActivityLogFilter(filters.FilterSet):
    timestamp_after = filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="gte")
    timestamp_before = filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = ActivityLog
        fields = [
            "source_ip",
            "destination_ip",
            "protocol",
            "event_type",
            "status",
            "source_vlan",
            "destination_vlan",
        ]


class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]
    filterset_class = ActivityLogFilter
    search_fields = ["source_ip", "destination_ip", "raw_message"]
    ordering_fields = ["timestamp", "created_at", "source_ip", "event_type"]


class BulkActivityLogView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["logs"], request=BulkActivityLogSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        serializer = BulkActivityLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = serializer.save()
        return Response({"created_logs": len(created)}, status=status.HTTP_201_CREATED)


class CSVUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(
        tags=["logs"],
        description="Upload activity logs from a CSV file using multipart/form-data field 'file'.",
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "CSV upload result",
                value={"created_logs": 25},
                response_only=True,
            )
        ],
    )
    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"detail": "Upload a CSV file using form field 'file'."}, status=400)
        try:
            rows = parse_csv_upload(uploaded_file)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        serializer = ActivityLogSerializer(data=rows, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"created_logs": len(serializer.data)}, status=status.HTTP_201_CREATED)


class JSONUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(
        tags=["logs"],
        description="Upload activity logs as a JSON array or an object with a 'logs' array.",
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "JSON logs",
                value={"logs": [{"timestamp": "2026-05-01T10:00:00Z", "source_ip": "192.168.20.15", "destination_ip": "192.168.30.10", "protocol": "TCP", "port": 22, "event_type": "ssh_login", "status": "failed"}]},
                request_only=True,
            ),
            OpenApiExample("JSON upload result", value={"created_logs": 1}, response_only=True),
        ],
    )
    def post(self, request):
        try:
            rows = parse_json_upload(request.FILES.get("file"), request.data)
        except (ValueError, TypeError) as exc:
            return Response({"detail": str(exc)}, status=400)
        serializer = ActivityLogSerializer(data=rows, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"created_logs": len(serializer.data)}, status=status.HTTP_201_CREATED)


class SyslogIngestView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(
        tags=["logs"],
        responses=ActivityLogSerializer,
        examples=[
            OpenApiExample(
                "Cisco ACL syslog",
                value={"message": "<189>May  1 10:00:01 R1 %SEC-6-IPACCESSLOGP: list ACL-IN denied tcp 192.168.20.15(4444) -> 192.168.30.10(22), 1 packet", "source_device": "R1-Core-Router"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        message = request.data.get("message")
        if not message:
            return Response({"detail": "Field 'message' is required."}, status=400)
        payload = parse_syslog_message(message, request.data.get("source_device", ""))
        serializer = ActivityLogSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        log = serializer.save()
        audit_log(request.user, "syslog_ingested", "ActivityLog", log.id, request)
        return Response(ActivityLogSerializer(log).data, status=status.HTTP_201_CREATED)


class BulkSyslogIngestView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(tags=["logs"], responses=OpenApiTypes.OBJECT)
    def post(self, request):
        messages = request.data.get("messages")
        if not isinstance(messages, list):
            return Response({"detail": "Field 'messages' must be a list."}, status=400)
        rows = [
            parse_syslog_message(item.get("message") if isinstance(item, dict) else str(item), item.get("source_device", "") if isinstance(item, dict) else "")
            for item in messages
        ]
        serializer = ActivityLogSerializer(data=rows, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        audit_log(request.user, "syslog_bulk_ingested", "ActivityLog", None, request, {"created_logs": len(rows)})
        return Response({"created_logs": len(rows)}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["logs"], responses=OpenApiTypes.OBJECT)
@api_view(["DELETE"])
@permission_classes([IsAdminUserForUnsafe])
def clear_logs(request):
    count, _ = ActivityLog.objects.all().delete()
    audit_log(request.user, "logs_cleared", "ActivityLog", None, request, {"deleted_records": count})
    return Response({"deleted_records": count})
