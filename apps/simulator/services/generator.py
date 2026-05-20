from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.logs.models import ActivityLog


class LogGenerator:
    def generate_ssh_bruteforce(self, source_ip="192.168.20.15", destination_ip="192.168.30.10", attempts=6, duration_seconds=30):
        start = timezone.now()
        logs = [
            ActivityLog(
                timestamp=start + timedelta(seconds=self._spread(index, attempts, duration_seconds)),
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_vlan=20,
                destination_vlan=30,
                protocol="TCP",
                port=22,
                event_type=ActivityLog.EventTypes.SSH_LOGIN,
                action="login",
                status="failed",
                raw_message="Simulated failed SSH login",
            )
            for index in range(attempts)
        ]
        return ActivityLog.objects.bulk_create(logs)

    def generate_port_scan(self, source_ip="192.168.20.15", destination_ip="192.168.30.10", ports_count=15, duration_seconds=10):
        start = timezone.now()
        ports = list(range(20, 20 + ports_count))
        logs = [
            ActivityLog(
                timestamp=start + timedelta(seconds=self._spread(index, ports_count, duration_seconds)),
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_vlan=20,
                destination_vlan=30,
                protocol="TCP",
                port=port,
                event_type=ActivityLog.EventTypes.PORT_CONNECTION,
                action="connect",
                status="attempted",
                raw_message=f"Simulated connection attempt to port {port}",
            )
            for index, port in enumerate(ports)
        ]
        return ActivityLog.objects.bulk_create(logs)

    def generate_icmp_flood(self, source_ip="192.168.20.15", destination_ip="192.168.30.10", packets_count=120, duration_seconds=60):
        start = timezone.now()
        logs = [
            ActivityLog(
                timestamp=start + timedelta(seconds=self._spread(index, packets_count, duration_seconds)),
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_vlan=20,
                destination_vlan=30,
                protocol="ICMP",
                event_type=ActivityLog.EventTypes.ICMP_PACKET,
                action="echo_request",
                status="sent",
                raw_message="Simulated ICMP echo request",
            )
            for index in range(packets_count)
        ]
        return ActivityLog.objects.bulk_create(logs)

    def generate_vlan_violation(self, source_ip="192.168.20.15", destination_ip="192.168.30.10", source_vlan=20, destination_vlan=30, count=1):
        now = timezone.now()
        logs = [
            ActivityLog(
                timestamp=now + timedelta(seconds=index),
                source_ip=source_ip,
                destination_ip=destination_ip,
                source_vlan=source_vlan,
                destination_vlan=destination_vlan,
                protocol="TCP",
                port=443,
                event_type=ActivityLog.EventTypes.VLAN_TRAFFIC,
                action="connect",
                status="allowed",
                raw_message="Simulated abnormal inter-VLAN traffic",
            )
            for index in range(count)
        ]
        return ActivityLog.objects.bulk_create(logs)

    def generate_arp_spoofing(self, ip_address="192.168.20.1", mac_a="00:11:22:33:44:55", mac_b="66:77:88:99:AA:BB"):
        now = timezone.now()
        logs = [
            ActivityLog(
                timestamp=now,
                source_ip=ip_address,
                protocol="ARP",
                event_type=ActivityLog.EventTypes.ARP_EVENT,
                action="reply",
                status="observed",
                raw_message="Simulated ARP reply",
                metadata={"ip_address": ip_address, "mac_address": mac_a, "is_unsolicited_reply": False},
            ),
            ActivityLog(
                timestamp=now + timedelta(seconds=5),
                source_ip=ip_address,
                protocol="ARP",
                event_type=ActivityLog.EventTypes.ARP_EVENT,
                action="reply",
                status="observed",
                raw_message="Simulated conflicting ARP reply",
                metadata={"ip_address": ip_address, "mac_address": mac_b, "is_unsolicited_reply": True},
            ),
        ]
        return ActivityLog.objects.bulk_create(logs)

    def generate_mixed(self):
        created = []
        created.extend(self.generate_ssh_bruteforce())
        created.extend(self.generate_port_scan())
        created.extend(self.generate_icmp_flood())
        created.extend(self.generate_vlan_violation())
        created.extend(self.generate_arp_spoofing())
        return created

    @staticmethod
    def _spread(index, total, duration_seconds):
        if total <= 1:
            return 0
        return int(index * max(duration_seconds, 1) / max(total - 1, 1))
