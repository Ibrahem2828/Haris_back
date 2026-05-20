from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class BulkActivityLogSerializer(serializers.Serializer):
    logs = ActivityLogSerializer(many=True)

    def create(self, validated_data):
        items = [ActivityLog(**item) for item in validated_data["logs"]]
        return ActivityLog.objects.bulk_create(items)
