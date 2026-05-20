from django.db import models

from apps.common.models import TimeStampedModel


class ActivityLog(TimeStampedModel):
    class EventTypes(models.TextChoices):
        SSH_LOGIN = "ssh_login", "SSH Login"
        PORT_CONNECTION = "port_connection", "Port Connection"
        ICMP_PACKET = "icmp_packet", "ICMP Packet"
        VLAN_TRAFFIC = "vlan_traffic", "VLAN Traffic"
        ARP_EVENT = "arp_event", "ARP Event"
        UNKNOWN = "unknown", "Unknown"

    timestamp = models.DateTimeField(db_index=True)
    source_ip = models.GenericIPAddressField(db_index=True)
    destination_ip = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    source_vlan = models.IntegerField(null=True, blank=True, db_index=True)
    destination_vlan = models.IntegerField(null=True, blank=True, db_index=True)
    protocol = models.CharField(max_length=32, blank=True, db_index=True)
    port = models.PositiveIntegerField(null=True, blank=True)
    action = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=64, blank=True, db_index=True)
    event_type = models.CharField(max_length=32, choices=EventTypes.choices, default=EventTypes.UNKNOWN, db_index=True)
    raw_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["source_ip", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.event_type} {self.source_ip} -> {self.destination_ip or '-'}"
