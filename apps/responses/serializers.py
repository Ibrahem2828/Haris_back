from rest_framework import serializers

from .models import ResponseAction
from .services.generator import ResponseGenerator


class ResponseActionSerializer(serializers.ModelSerializer):
    alert_attack_type = serializers.CharField(source="alert.attack_type", read_only=True)
    alert_source_ip = serializers.CharField(source="alert.source_ip", read_only=True)

    class Meta:
        model = ResponseAction
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "approved_by", "approved_at", "executed_at"]


class ResponseRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class ResponseExecutedSerializer(serializers.Serializer):
    execution_notes = serializers.CharField(required=False, allow_blank=True)


class ResponsePreviewSerializer(serializers.Serializer):
    attack_type = serializers.ChoiceField(choices=["ssh_bruteforce", "port_scan", "icmp_flood", "vlan_violation", "arp_spoofing"])
    source_ip = serializers.IPAddressField()
    destination_ip = serializers.IPAddressField(required=False, allow_null=True)
    evidence = serializers.JSONField(required=False)

    def create_preview(self):
        data = self.validated_data
        return ResponseGenerator().preview(
            data["attack_type"],
            data["source_ip"],
            data.get("destination_ip"),
            data.get("evidence") or {},
        ).as_dict()
