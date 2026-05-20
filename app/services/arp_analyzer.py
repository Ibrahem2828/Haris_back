from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.core.constants import SEVERITY_CRITICAL, SEVERITY_LOW


class ARPAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def analyze_arp_event(self, event: models.Event) -> models.ARPAnalysis:
        if event.event_type != "arp_event" and event.protocol != "ARP":
            result = "Not an ARP event."
            severity = SEVERITY_LOW
            observation = "not_arp"
        elif self.detect_unsolicited_arp_reply(event):
            result = "Suspicious unsolicited ARP reply observed."
            severity = SEVERITY_CRITICAL
            observation = "unsolicited_arp_reply"
        elif self.detect_duplicate_ip_mac(event.source_ip, event.source_mac):
            result = "Same IP address observed with multiple MAC addresses."
            severity = SEVERITY_CRITICAL
            observation = "duplicate_ip_mac"
        else:
            result = "Normal ARP observation."
            severity = SEVERITY_LOW
            observation = "normal_arp"
        analysis = models.ARPAnalysis(
            ip_address=event.source_ip,
            mac_address=event.source_mac or "unknown",
            observation_type=observation,
            result=result,
            severity=severity,
            timestamp=event.timestamp,
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def detect_duplicate_ip_mac(self, ip_address: str, mac_address: str | None) -> bool:
        if not ip_address or not mac_address:
            return False
        count = (
            self.db.query(func.count(func.distinct(models.Event.source_mac)))
            .filter(models.Event.source_ip == ip_address, models.Event.source_mac.isnot(None))
            .scalar()
        )
        return count > 1

    def detect_unsolicited_arp_reply(self, event: models.Event) -> bool:
        return event.status in {"unsolicited_reply", "suspicious_reply"} or "unsolicited" in (event.raw_message or "").lower()

    def generate_arp_alert(self, event: models.Event):
        from app.services.detection_engine import DetectionEngine

        return DetectionEngine(self.db).analyze_event(event)
