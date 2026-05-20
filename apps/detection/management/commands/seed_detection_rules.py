from django.core.management.base import BaseCommand

from apps.detection.models import DetectionRule


DEFAULT_RULES = [
    {
        "name": "SSH Brute Force",
        "rule_type": "ssh_bruteforce",
        "description": "Detect repeated failed SSH login attempts from the same source IP.",
        "threshold": 5,
        "time_window_seconds": 60,
        "severity": "high",
        "parameters": {},
    },
    {
        "name": "Port Scan",
        "rule_type": "port_scan",
        "description": "Detect many distinct destination ports from one source to one target in a short window.",
        "threshold": 10,
        "time_window_seconds": 10,
        "severity": "high",
        "parameters": {},
    },
    {
        "name": "ICMP Flood",
        "rule_type": "icmp_flood",
        "description": "Detect high volume ICMP traffic from one source.",
        "threshold": 100,
        "time_window_seconds": 60,
        "severity": "critical",
        "parameters": {},
    },
    {
        "name": "VLAN Violation",
        "rule_type": "vlan_violation",
        "description": "Detect traffic between blocked VLAN pairs.",
        "threshold": 1,
        "time_window_seconds": 60,
        "severity": "medium",
        "parameters": {"blocked_pairs": [{"source_vlan": 20, "destination_vlan": 30}]},
    },
    {
        "name": "ARP Spoofing Indicator",
        "rule_type": "arp_spoofing",
        "description": "Detect conflicting IP/MAC observations or unsolicited ARP replies.",
        "threshold": 1,
        "time_window_seconds": 60,
        "severity": "high",
        "parameters": {},
    },
]


class Command(BaseCommand):
    help = "Seed default Haris Phase 1 detection rules."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for rule in DEFAULT_RULES:
            _, was_created = DetectionRule.objects.update_or_create(
                rule_type=rule["rule_type"],
                defaults={**rule, "is_active": True},
            )
            created += int(was_created)
            updated += int(not was_created)
        self.stdout.write(self.style.SUCCESS(f"Detection rules ready. created={created}, updated={updated}"))
