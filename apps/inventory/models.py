from django.db import models

from apps.common.models import TimeStampedModel


class Network(TimeStampedModel):
    name = models.CharField(max_length=120)
    cidr = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.cidr})"


class VLAN(TimeStampedModel):
    vlan_id = models.PositiveIntegerField()
    name = models.CharField(max_length=120)
    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="vlans")
    gateway_ip = models.GenericIPAddressField()
    purpose = models.CharField(max_length=255, blank=True)
    is_restricted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["network", "vlan_id"], name="unique_vlan_per_network")
        ]

    def __str__(self):
        return f"VLAN {self.vlan_id} - {self.name}"


class Device(TimeStampedModel):
    class DeviceTypes(models.TextChoices):
        ROUTER = "router", "Router"
        SWITCH = "switch", "Switch"
        SERVER = "server", "Server"
        PC = "pc", "PC"
        LAPTOP = "laptop", "Laptop"
        ATTACKER = "attacker", "Attacker"
        SECURITY_SERVER = "security_server", "Security Server"
        SYSLOG_SERVER = "syslog_server", "Syslog Server"
        UNKNOWN = "unknown", "Unknown"

    class Statuses(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPICIOUS = "suspicious", "Suspicious"
        UNDER_ATTACK = "under_attack", "Under Attack"
        UNKNOWN = "unknown", "Unknown"

    name = models.CharField(max_length=120)
    ip_address = models.GenericIPAddressField(db_index=True)
    mac_address = models.CharField(max_length=32, blank=True)
    device_type = models.CharField(max_length=32, choices=DeviceTypes.choices, default=DeviceTypes.UNKNOWN)
    vlan = models.ForeignKey(VLAN, on_delete=models.SET_NULL, null=True, blank=True, related_name="devices")
    status = models.CharField(max_length=32, choices=Statuses.choices, default=Statuses.UNKNOWN)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"
