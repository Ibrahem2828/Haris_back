from django.db import models


class ARPSample(models.Model):
    class ARPTypes(models.TextChoices):
        REQUEST = "request", "Request"
        REPLY = "reply", "Reply"

    timestamp = models.DateTimeField()
    ip_address = models.GenericIPAddressField(db_index=True)
    mac_address = models.CharField(max_length=32)
    arp_type = models.CharField(max_length=16, choices=ARPTypes.choices)
    is_unsolicited = models.BooleanField(default=False)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.ip_address} {self.mac_address}"
