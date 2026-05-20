from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import decorators, generics, response, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.audit.services import audit_log
from apps.common.permissions import CanRunDetection, IsSecurityEngineerOrAdmin, ReadOnlyOrAdmin
from apps.common.serializers import EmptySerializer

from .models import DetectionJob, DetectionRule
from .serializers import DetectionJobSerializer, DetectionRuleSerializer, DetectionRunSerializer
from .services.engine import DetectionEngine
from .tasks import run_detection_job


class DetectionRuleViewSet(viewsets.ModelViewSet):
    queryset = DetectionRule.objects.all().order_by("rule_type")
    serializer_class = DetectionRuleSerializer
    permission_classes = [ReadOnlyOrAdmin | IsSecurityEngineerOrAdmin]
    filterset_fields = ["rule_type", "severity", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["rule_type", "severity", "created_at"]

    def perform_create(self, serializer):
        rule = serializer.save()
        audit_log(self.request.user, "rule_created", "DetectionRule", rule.id, self.request)

    def perform_update(self, serializer):
        rule = serializer.save()
        audit_log(self.request.user, "rule_updated", "DetectionRule", rule.id, self.request)

    def perform_destroy(self, instance):
        rule_id = instance.id
        instance.delete()
        audit_log(self.request.user, "rule_deleted", "DetectionRule", rule_id, self.request)

    @decorators.action(detail=True, methods=["patch"])
    def toggle(self, request, pk=None):
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save(update_fields=["is_active", "updated_at"])
        return response.Response(DetectionRuleSerializer(rule).data)


class DetectionJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DetectionJob.objects.all()
    serializer_class = DetectionJobSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "started_at", "finished_at"]

    @decorators.action(detail=True, methods=["post"], permission_classes=[CanRunDetection])
    def rerun(self, request, pk=None):
        source_job = self.get_object()
        job = DetectionEngine().run_detection(
            from_timestamp=source_job.from_timestamp,
            to_timestamp=source_job.to_timestamp,
            rule_types=source_job.rules_requested,
            triggered_by=request.user,
            mode=DetectionJob.Modes.SYNC,
        )
        return response.Response(DetectionJobSerializer(job).data, status=status.HTTP_201_CREATED)


class DetectionRunView(APIView):
    permission_classes = [CanRunDetection]

    @extend_schema(
        tags=["detection"],
        request=DetectionRunSerializer,
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Async port scan detection",
                value={"from": "2026-05-01T10:00:00Z", "to": "2026-05-01T11:00:00Z", "rules": ["port_scan"], "async": True},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = DetectionRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data.get("async_run"):
            job = DetectionJob.objects.create(
                status=DetectionJob.Statuses.PENDING,
                from_timestamp=data.get("from_timestamp"),
                to_timestamp=data.get("to_timestamp"),
                rules_requested=data.get("rules") or [],
                triggered_by=request.user,
                mode=DetectionJob.Modes.ASYNC,
            )
            task = run_detection_job.delay(job.id)
            job.celery_task_id = getattr(task, "id", None)
            job.save(update_fields=["celery_task_id", "updated_at"])
            audit_log(request.user, "detection_run_queued", "DetectionJob", job.id, request, {"task_id": job.celery_task_id})
            return response.Response(
                {"job_id": job.id, "status": job.status, "task_id": job.celery_task_id, "logs_processed": job.logs_processed, "alerts_created": job.alerts_created},
                status=status.HTTP_202_ACCEPTED,
            )
        job = DetectionEngine().run_detection(
            from_timestamp=data.get("from_timestamp"),
            to_timestamp=data.get("to_timestamp"),
            rule_types=data.get("rules"),
            triggered_by=request.user,
            mode=DetectionJob.Modes.SYNC,
        )
        return response.Response(
            {
                "job_id": job.id,
                "status": job.status,
                "logs_processed": job.logs_processed,
                "alerts_created": job.alerts_created,
                "error_message": job.error_message,
            },
            status=status.HTTP_201_CREATED,
        )


class DetectionSchedulePreviewView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(tags=["detection"], responses=OpenApiTypes.OBJECT)
    def post(self, request):
        return response.Response({"message": "Scheduled detection is Celery-ready. Configure celery beat in deployment for periodic execution."})
