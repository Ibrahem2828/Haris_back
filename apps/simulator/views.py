from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.serializers import EmptySerializer
from .services.generator import LogGenerator


class BaseGenerateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer
    generator_method = None
    success_message = "Logs generated successfully"

    @extend_schema(
        tags=["simulator"],
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                "Port scan generation",
                value={"source_ip": "192.168.20.15", "destination_ip": "192.168.30.10", "ports_count": 15, "duration_seconds": 10},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        method = getattr(LogGenerator(), self.generator_method)
        created = method(**request.data)
        return Response(
            {"created_logs": len(created), "message": self.success_message},
            status=status.HTTP_201_CREATED,
        )


class GenerateSSHBruteforceView(BaseGenerateView):
    generator_method = "generate_ssh_bruteforce"
    success_message = "SSH brute force logs generated successfully"


class GeneratePortScanView(BaseGenerateView):
    generator_method = "generate_port_scan"
    success_message = "Port scan logs generated successfully"


class GenerateICMPFloodView(BaseGenerateView):
    generator_method = "generate_icmp_flood"
    success_message = "ICMP flood logs generated successfully"


class GenerateVLANViolationView(BaseGenerateView):
    generator_method = "generate_vlan_violation"
    success_message = "VLAN violation logs generated successfully"


class GenerateARPSpoofingView(BaseGenerateView):
    generator_method = "generate_arp_spoofing"
    success_message = "ARP spoofing logs generated successfully"


class GenerateMixedView(BaseGenerateView):
    generator_method = "generate_mixed"
    success_message = "Mixed attack logs generated successfully"
