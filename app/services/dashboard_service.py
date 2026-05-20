from collections import Counter

from sqlalchemy.orm import Session

from app import models
from app.core.constants import ALERT_STATUS_RESOLVED


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def summary(self):
        alerts = self.db.query(models.Alert).all()
        events = self.db.query(models.Event).all()
        attack_counter = Counter(alert.attack_type for alert in alerts)
        return {
            "total_events": len(events),
            "total_alerts": len(alerts),
            "critical_alerts": sum(1 for alert in alerts if alert.severity == "Critical"),
            "high_alerts": sum(1 for alert in alerts if alert.severity == "High"),
            "medium_alerts": sum(1 for alert in alerts if alert.severity == "Medium"),
            "low_alerts": sum(1 for alert in alerts if alert.severity == "Low"),
            "normal_events": sum(1 for event in events if not event.is_suspicious),
            "suspicious_events": sum(1 for event in events if event.is_suspicious),
            "latest_alerts": [
                {"id": alert.id, "attack_type": alert.attack_type, "severity": alert.severity, "source_ip": alert.source_ip}
                for alert in self.db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(5).all()
            ],
            "most_common_attack": attack_counter.most_common(1)[0][0] if attack_counter else None,
            "system_status": self.system_status(alerts),
        }

    def statistics(self):
        return {
            "events_by_protocol": dict(Counter(event.protocol for event in self.db.query(models.Event).all())),
            "alerts_by_status": dict(Counter(alert.status for alert in self.db.query(models.Alert).all())),
            "responses_by_status": dict(Counter(response.execution_status for response in self.db.query(models.Response).all())),
        }

    def attack_distribution(self):
        return dict(Counter(alert.attack_type for alert in self.db.query(models.Alert).all()))

    def network_status(self):
        unresolved = self.db.query(models.Alert).filter(models.Alert.status != ALERT_STATUS_RESOLVED).count()
        return {
            "status": "Critical" if self.db.query(models.Alert).filter(models.Alert.severity == "Critical", models.Alert.status != ALERT_STATUS_RESOLVED).count() else "Warning" if unresolved else "Normal",
            "open_alerts": unresolved,
            "suspicious_events": self.db.query(models.Event).filter(models.Event.is_suspicious.is_(True)).count(),
        }

    @staticmethod
    def system_status(alerts):
        open_alerts = [alert for alert in alerts if alert.status != ALERT_STATUS_RESOLVED]
        if any(alert.severity == "Critical" for alert in open_alerts):
            return "Critical"
        if any(alert.severity == "High" for alert in open_alerts):
            return "Warning"
        return "Normal"
