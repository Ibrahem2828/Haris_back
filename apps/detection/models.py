from django.db import models

from apps.common.models import TimeStampedModel


class DetectionRule(TimeStampedModel):
    class RuleTypes(models.TextChoices):
        SSH_BRUTEFORCE = "ssh_bruteforce", "SSH Brute Force"
        PORT_SCAN = "port_scan", "Port Scan"
        ICMP_FLOOD = "icmp_flood", "ICMP Flood"
        VLAN_VIOLATION = "vlan_violation", "VLAN Violation"
        ARP_SPOOFING = "arp_spoofing", "ARP Spoofing"

    class Severities(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    name = models.CharField(max_length=160)
    rule_type = models.CharField(max_length=32, choices=RuleTypes.choices, unique=True)
    description = models.TextField(blank=True)
    threshold = models.PositiveIntegerField()
    time_window_seconds = models.PositiveIntegerField()
    severity = models.CharField(max_length=16, choices=Severities.choices)
    is_active = models.BooleanField(default=True)
    parameters = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class DetectionJob(TimeStampedModel):
    class Statuses(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Modes(models.TextChoices):
        SYNC = "sync", "Sync"
        ASYNC = "async", "Async"
        SCHEDULED = "scheduled", "Scheduled"
        SIMULATOR = "simulator", "Simulator"

    status = models.CharField(max_length=16, choices=Statuses.choices, default=Statuses.PENDING)
    mode = models.CharField(max_length=16, choices=Modes.choices, default=Modes.SYNC)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    triggered_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="detection_jobs")
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    from_timestamp = models.DateTimeField(null=True, blank=True)
    to_timestamp = models.DateTimeField(null=True, blank=True)
    rules_requested = models.JSONField(default=list, blank=True)
    logs_processed = models.PositiveIntegerField(default=0)
    alerts_created = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Detection job #{self.pk} ({self.status})"
