from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = ["id", "actor", "actor_username", "action", "resource_type", "resource_id", "ip_address", "metadata", "created_at"]
