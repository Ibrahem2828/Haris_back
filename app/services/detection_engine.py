from abc import ABC, abstractmethod

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.core.constants import (
    ATTACK_ARP_SPOOFING,
    ATTACK_ICMP_FLOOD,
    ATTACK_PORT_SCAN,
    ATTACK_SSH_BRUTE_FORCE,
    ATTACK_VLAN_VIOLATION,
    BLOCKED_VLAN_PAIRS,
)
from app.services.alert_manager import AlertManager
from app.utils.time_window import window_start


class BaseDetectionRule(ABC):
    attack_type: str

    @abstractmethod
    def evaluate(self, event: models.Event, db_rule: models.DetectionRule, db: Session) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_description(self, event: models.Event, db_rule: models.DetectionRule, db: Session) -> str:
        raise NotImplementedError


class SSHBruteForceRule(BaseDetectionRule):
    attack_type = ATTACK_SSH_BRUTE_FORCE

    def evaluate(self, event, db_rule, db):
        if event.event_type != "ssh_login":
            return False
        if event.port != 22 and event.protocol not in {"SSH", "TCP"}:
            return False
        if event.status not in {"failed", "failed_login", "denied"}:
            return False
        count = (
            db.query(models.Event)
            .filter(
                models.Event.source_ip == event.source_ip,
                models.Event.event_type == "ssh_login",
                models.Event.status.in_(["failed", "failed_login", "denied"]),
                models.Event.timestamp >= window_start(event.timestamp, db_rule.time_window_seconds),
                models.Event.timestamp <= event.timestamp,
            )
            .count()
        )
        return count > db_rule.threshold

    def generate_description(self, event, db_rule, db):
        return f"SSH brute force detected from {event.source_ip}: more than {db_rule.threshold} failed login attempts in {db_rule.time_window_seconds} seconds."


class PortScanRule(BaseDetectionRule):
    attack_type = ATTACK_PORT_SCAN

    def evaluate(self, event, db_rule, db):
        if event.event_type != "port_connection" or event.port is None:
            return False
        distinct_ports = (
            db.query(models.Event.port)
            .filter(
                models.Event.source_ip == event.source_ip,
                models.Event.event_type == "port_connection",
                models.Event.port.isnot(None),
                models.Event.timestamp >= window_start(event.timestamp, db_rule.time_window_seconds),
                models.Event.timestamp <= event.timestamp,
            )
            .distinct()
            .count()
        )
        return distinct_ports > db_rule.threshold

    def generate_description(self, event, db_rule, db):
        return f"Port scan detected from {event.source_ip}: more than {db_rule.threshold} distinct ports in {db_rule.time_window_seconds} seconds."


class ICMPFloodRule(BaseDetectionRule):
    attack_type = ATTACK_ICMP_FLOOD

    def evaluate(self, event, db_rule, db):
        if event.protocol != "ICMP" and event.event_type != "icmp_packet":
            return False
        count = (
            db.query(models.Event)
            .filter(
                models.Event.source_ip == event.source_ip,
                (models.Event.protocol == "ICMP") | (models.Event.event_type == "icmp_packet"),
                models.Event.timestamp >= window_start(event.timestamp, db_rule.time_window_seconds),
                models.Event.timestamp <= event.timestamp,
            )
            .count()
        )
        return count > db_rule.threshold

    def generate_description(self, event, db_rule, db):
        return f"ICMP flood detected from {event.source_ip}: more than {db_rule.threshold} ICMP packets in {db_rule.time_window_seconds} seconds."


class VLANViolationRule(BaseDetectionRule):
    attack_type = ATTACK_VLAN_VIOLATION

    def evaluate(self, event, db_rule, db):
        if event.event_type != "vlan_traffic":
            return False
        return (event.source_vlan, event.destination_vlan) in BLOCKED_VLAN_PAIRS

    def generate_description(self, event, db_rule, db):
        return f"Unauthorized VLAN traffic detected from VLAN {event.source_vlan} to VLAN {event.destination_vlan}."


class ARPSpoofingRule(BaseDetectionRule):
    attack_type = ATTACK_ARP_SPOOFING

    def evaluate(self, event, db_rule, db):
        if event.event_type != "arp_event" and event.protocol != "ARP":
            return False
        if event.status in {"unsolicited_reply", "suspicious_reply"}:
            return True
        if not event.source_mac:
            return False
        mac_count = (
            db.query(func.count(func.distinct(models.Event.source_mac)))
            .filter(
                models.Event.source_ip == event.source_ip,
                models.Event.source_mac.isnot(None),
                models.Event.timestamp >= window_start(event.timestamp, db_rule.time_window_seconds),
                models.Event.timestamp <= event.timestamp,
            )
            .scalar()
        )
        return mac_count > 1

    def generate_description(self, event, db_rule, db):
        return f"ARP spoofing indicator detected for IP {event.source_ip}: duplicate MAC mapping or suspicious ARP reply."


class DetectionEngine:
    def __init__(self, db: Session):
        self.db = db
        self.alert_manager = AlertManager(db)
        self.rule_classes = {
            ATTACK_SSH_BRUTE_FORCE: SSHBruteForceRule(),
            ATTACK_PORT_SCAN: PortScanRule(),
            ATTACK_ICMP_FLOOD: ICMPFloodRule(),
            ATTACK_VLAN_VIOLATION: VLANViolationRule(),
            ATTACK_ARP_SPOOFING: ARPSpoofingRule(),
        }

    def load_rules(self):
        return self.db.query(models.DetectionRule).filter(models.DetectionRule.enabled.is_(True)).all()

    def analyze_event(self, event: models.Event) -> list[models.Alert]:
        created_alerts = []
        for db_rule in self.load_rules():
            rule = self.rule_classes.get(db_rule.attack_type)
            if not rule:
                continue
            if rule.evaluate(event, db_rule, self.db):
                description = rule.generate_description(event, db_rule, self.db)
                alert = self.create_alert(event, db_rule, description)
                if alert not in created_alerts:
                    created_alerts.append(alert)
        return created_alerts

    def analyze_all_events(self) -> tuple[int, int]:
        events = self.db.query(models.Event).order_by(models.Event.timestamp.asc()).all()
        before = self.db.query(models.Alert).count()
        for event in events:
            self.analyze_event(event)
        after = self.db.query(models.Alert).count()
        return len(events), after - before

    def create_alert(self, event: models.Event, rule: models.DetectionRule, description: str):
        return self.alert_manager.create_alert(event, rule, description)

    def send_to_response_module(self, alert: models.Alert):
        return alert.response
