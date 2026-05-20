from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.serializers import EmptySerializer
from apps.detection.services.engine import DetectionEngine
from apps.logs.models import ActivityLog

from .models import ARPSample
from .serializers import ARPSampleSerializer


class ARPSampleViewSet(viewsets.ModelViewSet):
    queryset = ARPSample.objects.all()
    serializer_class = ARPSampleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["ip_address", "mac_address", "arp_type", "is_unsolicited", "source_ip"]
    ordering_fields = ["timestamp", "created_at", "ip_address"]


class ARPAnalyzeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(tags=["arp"], responses=OpenApiTypes.OBJECT)
    def post(self, request):
        sample_ids = request.data.get("sample_ids")
        samples = ARPSample.objects.all()
        if sample_ids:
            samples = samples.filter(id__in=sample_ids)
        logs = [
            ActivityLog(
                timestamp=sample.timestamp,
                source_ip=sample.source_ip or sample.ip_address,
                protocol="ARP",
                event_type=ActivityLog.EventTypes.ARP_EVENT,
                action=sample.arp_type,
                status="observed",
                raw_message="ARP sample analyzed",
                metadata={
                    "ip_address": sample.ip_address,
                    "mac_address": sample.mac_address,
                    "is_unsolicited_reply": sample.is_unsolicited and sample.arp_type == ARPSample.ARPTypes.REPLY,
                    "arp_sample_id": sample.id,
                },
            )
            for sample in samples
        ]
        ActivityLog.objects.bulk_create(logs)
        job = DetectionEngine().run_detection(rule_types=["arp_spoofing"])
        return Response(
            {
                "created_logs": len(logs),
                "job_id": job.id,
                "status": job.status,
                "alerts_created": job.alerts_created,
            },
            status=status.HTTP_201_CREATED,
        )
