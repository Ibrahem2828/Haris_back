from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.detection.services.engine import DetectionEngine
from apps.incidents.models import Alert
from apps.inventory.models import Device, Network, VLAN
from apps.logs.models import ActivityLog
from apps.simulator.services.generator import LogGenerator


class Command(BaseCommand):
    help = "Seed demo inventory and sample attack logs."

    def handle(self, *args, **options):
        call_command("seed_detection_rules")

        network, _ = Network.objects.get_or_create(
            name="Haris Lab Network",
            defaults={"cidr": "192.168.0.0/16", "description": "Demo network for Haris Phase 1."},
        )
        vlan_specs = [
            (10, "Management", "192.168.10.1", "Network management", True),
            (20, "Users", "192.168.20.1", "User endpoints", False),
            (30, "Servers", "192.168.30.1", "Server subnet", True),
            (40, "Security", "192.168.40.1", "Security tooling", True),
        ]
        vlans = {}
        for vlan_id, name, gateway, purpose, restricted in vlan_specs:
            vlan, _ = VLAN.objects.get_or_create(
                network=network,
                vlan_id=vlan_id,
                defaults={"name": name, "gateway_ip": gateway, "purpose": purpose, "is_restricted": restricted},
            )
            vlans[vlan_id] = vlan

        devices = [
            ("R1-Core-Router", "192.168.10.1", "router", 10),
            ("SW1-Users", "192.168.10.2", "switch", 10),
            ("SW2-Servers", "192.168.10.3", "switch", 10),
            ("SW3-Test", "192.168.10.4", "switch", 10),
            ("SRV-Web", "192.168.30.10", "server", 30),
            ("SRV-Haris", "192.168.40.5", "security_server", 40),
            ("PC-User-01", "192.168.20.15", "pc", 20),
            ("PC-Attacker", "192.168.20.200", "attacker", 20),
            ("Syslog-Server", "192.168.40.20", "syslog_server", 40),
        ]
        for name, ip, device_type, vlan_id in devices:
            Device.objects.get_or_create(
                ip_address=ip,
                defaults={"name": name, "device_type": device_type, "vlan": vlans[vlan_id], "status": "active"},
            )

        before_alert_ids = set(Alert.objects.values_list("id", flat=True))
        created = LogGenerator().generate_mixed()
        for log in ActivityLog.objects.filter(id__in=[item.id for item in created]):
            metadata = dict(log.metadata)
            metadata["is_demo"] = True
            log.metadata = metadata
            log.save(update_fields=["metadata", "updated_at"])
        job = DetectionEngine().run_detection(rule_types=["ssh_bruteforce", "port_scan", "icmp_flood", "vlan_violation", "arp_spoofing"], mode="simulator")
        for alert in Alert.objects.exclude(id__in=before_alert_ids):
            evidence = dict(alert.evidence)
            evidence["is_demo"] = True
            alert.evidence = evidence
            alert.save(update_fields=["evidence", "updated_at"])
        self.stdout.write(self.style.SUCCESS(f"Demo data ready. created_logs={len(created)}, detection_job={job.id}, alerts_created={job.alerts_created}"))
