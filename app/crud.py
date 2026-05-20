from datetime import datetime

from sqlalchemy.orm import Session

from app import models, schemas


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    user = models.User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session):
    return db.query(models.User).order_by(models.User.id).all()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_event(db: Session, payload: schemas.EventCreate) -> models.Event:
    data = payload.model_dump()
    if data.get("timestamp") is None:
        data["timestamp"] = datetime.utcnow()
    data["protocol"] = (data.get("protocol") or "UNKNOWN").upper()
    event = models.Event(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def list_events(db: Session):
    return db.query(models.Event).order_by(models.Event.timestamp.desc()).all()


def create_rule(db: Session, payload: schemas.DetectionRuleCreate) -> models.DetectionRule:
    rule = models.DetectionRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(db: Session, rule: models.DetectionRule, payload: schemas.DetectionRuleUpdate):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


def seed_defaults(db: Session):
    from app.services.log_generator import LogGenerator

    if db.query(models.User).count() == 0:
        db.add_all(
            [
                models.User(name="Network Administrator", username="network_admin", role="network_admin"),
                models.User(name="Security Engineer", username="security_engineer", role="security_engineer"),
                models.User(name="Student Researcher", username="student", role="student"),
            ]
        )
    if db.query(models.DetectionRule).count() == 0:
        db.add_all(
            [
                models.DetectionRule(name="SSH Brute Force", description="More than 5 failed SSH login attempts from the same source IP within 60 seconds.", attack_type="ssh_bruteforce", threshold=5, time_window_seconds=60, severity="High", enabled=True),
                models.DetectionRule(name="Port Scan", description="More than 10 distinct ports contacted by the same source IP within 10 seconds.", attack_type="port_scan", threshold=10, time_window_seconds=10, severity="High", enabled=True),
                models.DetectionRule(name="ICMP Flood", description="More than 100 ICMP packets from the same source IP within 60 seconds.", attack_type="icmp_flood", threshold=100, time_window_seconds=60, severity="High", enabled=True),
                models.DetectionRule(name="VLAN Violation", description="Unauthorized traffic between VLAN 20 and VLAN 30.", attack_type="vlan_violation", threshold=1, time_window_seconds=60, severity="High", enabled=True),
                models.DetectionRule(name="ARP Spoofing Indicator", description="Same IP observed with multiple MAC addresses or suspicious ARP reply.", attack_type="arp_spoofing", threshold=1, time_window_seconds=60, severity="Critical", enabled=True),
            ]
        )
    db.commit()
    if db.query(models.Event).count() == 0:
        LogGenerator(db).generate_normal(count=5, created_by=None)
