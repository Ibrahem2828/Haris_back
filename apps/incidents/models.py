from django.db import models

from apps.common.models import TimeStampedModel


class Alert(TimeStampedModel):
    class Severities(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Statuses(models.TextChoices):
        NEW = "new", "New"
        REVIEWING = "reviewing", "Reviewing"
        RESPONSE_SUGGESTED = "response_suggested", "Response Suggested"
        WAITING_APPROVAL = "waiting_approval", "Waiting Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        RESOLVED = "resolved", "Resolved"
        FALSE_POSITIVE = "false_positive", "False Positive"
        CLOSED = "closed", "Closed"

    rule = models.ForeignKey("detection.DetectionRule", on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")
    attack_type = models.CharField(max_length=64, db_index=True)
    source_ip = models.GenericIPAddressField(db_index=True)
    destination_ip = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    severity = models.CharField(max_length=16, choices=Severities.choices, db_index=True)
    status = models.CharField(max_length=32, choices=Statuses.choices, default=Statuses.NEW, db_index=True)
    description = models.TextField()
    evidence = models.JSONField(default=dict, blank=True)
    first_seen = models.DateTimeField(db_index=True)
    last_seen = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["attack_type", "source_ip", "created_at"]),
        ]

    def __str__(self):
        return f"{self.attack_type} from {self.source_ip}"


class AlertTimeline(models.Model):
    class EventTypes(models.TextChoices):
        CREATED = "created", "Created"
        STATUS_CHANGED = "status_changed", "Status Changed"
        RESPONSE_GENERATED = "response_generated", "Response Generated"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        EXECUTED = "executed", "Executed"
        RESOLVED = "resolved", "Resolved"
        FALSE_POSITIVE = "false_positive", "False Positive"
        CLOSED = "closed", "Closed"
        NOTE = "note", "Note"

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="timeline")
    event_type = models.CharField(max_length=32, choices=EventTypes.choices)
    old_status = models.CharField(max_length=32, blank=True, null=True)
    new_status = models.CharField(max_length=32, blank=True, null=True)
    message = models.TextField(blank=True)
    actor = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.alert_id} {self.event_type}"
