from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models


class LogGenerator:
    def __init__(self, db: Session):
        self.db = db

    def _record_simulation(self, simulation_type: str, description: str, created_by: int | None):
        simulation = models.Simulation(
            simulation_type=simulation_type,
            description=description,
            status="Completed",
            created_by=created_by,
        )
        self.db.add(simulation)
        self.db.commit()
        self.db.refresh(simulation)
        return simulation

    def _bulk_create(self, events: list[models.Event], simulation_type: str, description: str, created_by: int | None):
        self.db.add_all(events)
        self._record_simulation(simulation_type, description, created_by)
        self.db.commit()
        for event in events:
            self.db.refresh(event)
        return events

    def generate_normal(self, count: int = 10, created_by: int | None = None):
        now = datetime.utcnow()
        events = [
            models.Event(
                timestamp=now + timedelta(seconds=i),
                source_ip=f"192.168.10.{10 + i}",
                destination_ip="192.168.30.10",
                protocol="TCP",
                port=443,
                event_type="normal_traffic",
                status="allowed",
                source_vlan=10,
                destination_vlan=30,
                raw_message="Normal HTTPS traffic",
            )
            for i in range(count)
        ]
        return self._bulk_create(events, "normal", "Generated normal network traffic.", created_by)

    def generate_ssh_bruteforce(self, source_ip: str = "192.168.20.15", destination_ip: str = "192.168.30.10", attempts: int = 6, created_by: int | None = None):
        now = datetime.utcnow()
        events = [
            models.Event(timestamp=now + timedelta(seconds=i * 5), source_ip=source_ip, destination_ip=destination_ip, protocol="SSH", port=22, event_type="ssh_login", status="failed_login", source_vlan=20, destination_vlan=30, raw_message="Failed SSH login")
            for i in range(attempts)
        ]
        return self._bulk_create(events, "ssh_bruteforce", "Generated SSH brute force events.", created_by)

    def generate_port_scan(self, source_ip: str = "192.168.20.15", destination_ip: str = "192.168.30.10", ports_count: int = 12, created_by: int | None = None):
        now = datetime.utcnow()
        events = [
            models.Event(timestamp=now + timedelta(milliseconds=i * 500), source_ip=source_ip, destination_ip=destination_ip, protocol="TCP", port=20 + i, event_type="port_connection", status="attempted", source_vlan=20, destination_vlan=30, raw_message=f"Connection attempt to port {20 + i}")
            for i in range(ports_count)
        ]
        return self._bulk_create(events, "port_scan", "Generated port scan events.", created_by)

    def generate_icmp_flood(self, source_ip: str = "192.168.20.50", destination_ip: str = "192.168.30.10", count: int = 101, created_by: int | None = None):
        now = datetime.utcnow()
        events = [
            models.Event(timestamp=now + timedelta(milliseconds=i * 300), source_ip=source_ip, destination_ip=destination_ip, protocol="ICMP", event_type="icmp_packet", status="sent", source_vlan=20, destination_vlan=30, raw_message="ICMP echo request")
            for i in range(count)
        ]
        return self._bulk_create(events, "icmp_flood", "Generated ICMP flood events.", created_by)

    def generate_vlan_violation(self, source_ip: str = "192.168.20.25", destination_ip: str = "192.168.30.20", created_by: int | None = None):
        event = models.Event(timestamp=datetime.utcnow(), source_ip=source_ip, destination_ip=destination_ip, protocol="TCP", port=445, event_type="vlan_traffic", status="unauthorized", source_vlan=20, destination_vlan=30, raw_message="Unauthorized VLAN 20 to VLAN 30 traffic")
        return self._bulk_create([event], "vlan_violation", "Generated VLAN violation event.", created_by)

    def generate_arp_spoofing(self, ip_address: str = "192.168.20.1", created_by: int | None = None):
        now = datetime.utcnow()
        events = [
            models.Event(timestamp=now, source_ip=ip_address, protocol="ARP", event_type="arp_event", status="reply", source_mac="00:11:22:33:44:55", raw_message="ARP reply for gateway"),
            models.Event(timestamp=now + timedelta(seconds=3), source_ip=ip_address, protocol="ARP", event_type="arp_event", status="unsolicited_reply", source_mac="66:77:88:99:AA:BB", raw_message="Suspicious unsolicited ARP reply"),
        ]
        return self._bulk_create(events, "arp_spoofing", "Generated ARP spoofing indicators.", created_by)

    def generate_all(self, created_by: int | None = None):
        events = []
        events.extend(self.generate_normal(created_by=created_by))
        events.extend(self.generate_ssh_bruteforce(created_by=created_by))
        events.extend(self.generate_port_scan(created_by=created_by))
        events.extend(self.generate_icmp_flood(created_by=created_by))
        events.extend(self.generate_vlan_violation(created_by=created_by))
        events.extend(self.generate_arp_spoofing(created_by=created_by))
        return events
