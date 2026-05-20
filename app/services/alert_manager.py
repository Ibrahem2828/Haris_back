from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.core.constants import ALERT_STATUS_NEW, RESPONSE_PENDING
from app.services.response_module import ResponseModule


class AlertManager:
    def __init__(self, db: Session):
        self.db = db
        self.response_module = ResponseModule()

    def create_alert(self, event: models.Event, rule: models.DetectionRule, description: str) -> models.Alert:
        duplicate_since = datetime.utcnow() - timedelta(seconds=max(rule.time_window_seconds, 60))
        duplicate = (
            self.db.query(models.Alert)
            .filter(
                models.Alert.attack_type == rule.attack_type,
                models.Alert.source_ip == event.source_ip,
                models.Alert.destination_ip == event.destination_ip,
                models.Alert.matched_rule == rule.name,
                models.Alert.created_at >= duplicate_since,
            )
            .first()
        )
        if duplicate:
            return duplicate

        alert_like = type(
            "AlertLike",
            (),
            {"attack_type": rule.attack_type, "source_ip": event.source_ip, "destination_ip": event.destination_ip},
        )
        response_data = self.response_module.generate_response(alert_like)
        alert = models.Alert(
            event_id=event.id,
            attack_type=rule.attack_type,
            severity=rule.severity,
            source_ip=event.source_ip,
            destination_ip=event.destination_ip,
            matched_rule=rule.name,
            description=description,
            status=ALERT_STATUS_NEW,
            recommended_action=response_data["recommended_action"],
            cisco_command=response_data["cisco_command"],
        )
        event.is_suspicious = True
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        self.db.add(
            models.Response(
                alert_id=alert.id,
                action_type=response_data["recommended_action"],
                description=response_data["explanation"],
                cisco_command=response_data["cisco_command"],
                execution_status=RESPONSE_PENDING,
            )
        )
        self.db.commit()
        self.db.refresh(alert)
        return alert
