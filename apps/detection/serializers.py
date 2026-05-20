from rest_framework import serializers

from .models import DetectionJob, DetectionRule


class DetectionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionRule
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DetectionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionJob
        fields = "__all__"
        read_only_fields = ["id", "status", "started_at", "finished_at", "from_timestamp", "to_timestamp", "rules_requested", "logs_processed", "alerts_created", "error_message", "created_at", "updated_at", "mode", "celery_task_id", "triggered_by"]


class DetectionRunSerializer(serializers.Serializer):
    from_timestamp = serializers.DateTimeField(required=False, allow_null=True)
    to_timestamp = serializers.DateTimeField(required=False, allow_null=True)
    rules = serializers.ListField(
        child=serializers.ChoiceField(choices=DetectionRule.RuleTypes.choices),
        required=False,
        allow_empty=False,
    )
    async_run = serializers.BooleanField(required=False, default=False)

    def to_internal_value(self, data):
        mutable = dict(data)
        if "from" in mutable:
            mutable["from_timestamp"] = mutable.pop("from")
        if "to" in mutable:
            mutable["to_timestamp"] = mutable.pop("to")
        if "async" in mutable:
            mutable["async_run"] = mutable.pop("async")
        return super().to_internal_value(mutable)
