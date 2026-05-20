from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class ResponseAction(TimeStampedModel):
    class ActionTypes(models.TextChoices):
        BLOCK_IP = "block_ip", "Block IP"
        RATE_LIMIT = "rate_limit", "Rate Limit"
        ENHANCE_ACL = "enhance_acl", "Enhance ACL"
        SHUTDOWN_PORT = "shutdown_port", "Shutdown Port"
        INVESTIGATE = "investigate", "Investigate"
        MONITOR_ONLY = "monitor_only", "Monitor Only"
        ISOLATE_VLAN = "isolate_vlan", "Isolate VLAN"
        BIND_IP_MAC = "bind_ip_mac", "Bind IP/MAC"

    class RiskLevels(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class ApprovalStatuses(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        POSTPONED = "postponed", "Postponed"
        NOT_REQUIRED = "not_required", "Not Required"

    alert = models.OneToOneField("incidents.Alert", on_delete=models.CASCADE, related_name="response_action")
    action_type = models.CharField(max_length=32, choices=ActionTypes.choices)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    recommended_action = models.TextField()
    cisco_ios_commands = models.JSONField(default=list, blank=True)
    command_text = models.TextField(blank=True)
    risk_level = models.CharField(max_length=16, choices=RiskLevels.choices, default=RiskLevels.MEDIUM)
    requires_approval = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=16, choices=ApprovalStatuses.choices, default=ApprovalStatuses.PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_response_actions")
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True)
    executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField(null=True, blank=True)
    execution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.approval_status})"
