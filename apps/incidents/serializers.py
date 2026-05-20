from rest_framework import serializers

from .models import Alert, AlertTimeline


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AlertStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Alert.Statuses.choices)
    notes = serializers.CharField(required=False, allow_blank=True)


class AlertTimelineSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AlertTimeline
        fields = "__all__"
        read_only_fields = ["id", "alert", "event_type", "old_status", "new_status", "message", "actor", "actor_username", "created_at"]


class AlertNoteSerializer(serializers.Serializer):
    message = serializers.CharField()


class AlertReasonSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
