from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    username = Column(String(80), unique=True, index=True, nullable=False)
    role = Column(String(40), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    simulations = relationship("Simulation", back_populates="creator")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    source_ip = Column(String(45), index=True, nullable=False)
    destination_ip = Column(String(45), index=True, nullable=True)
    protocol = Column(String(20), index=True, nullable=False, default="UNKNOWN")
    port = Column(Integer, nullable=True)
    event_type = Column(String(60), index=True, nullable=False, default="unknown")
    status = Column(String(60), index=True, nullable=True)
    source_vlan = Column(Integer, nullable=True)
    destination_vlan = Column(Integer, nullable=True)
    source_mac = Column(String(40), nullable=True)
    destination_mac = Column(String(40), nullable=True)
    raw_message = Column(Text, nullable=True)
    is_suspicious = Column(Boolean, default=False, nullable=False)

    alerts = relationship("Alert", back_populates="event")


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    attack_type = Column(String(80), unique=True, index=True, nullable=False)
    threshold = Column(Integer, nullable=False)
    time_window_seconds = Column(Integer, nullable=False)
    severity = Column(String(20), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    attack_type = Column(String(80), index=True, nullable=False)
    severity = Column(String(20), index=True, nullable=False)
    source_ip = Column(String(45), index=True, nullable=False)
    destination_ip = Column(String(45), index=True, nullable=True)
    matched_rule = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(40), default="New", index=True, nullable=False)
    recommended_action = Column(Text, nullable=False)
    cisco_command = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    event = relationship("Event", back_populates="alerts")
    response = relationship("Response", back_populates="alert", uselist=False)


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    action_type = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    cisco_command = Column(Text, nullable=False)
    execution_status = Column(String(40), default="Pending", index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    alert = relationship("Alert", back_populates="response")


class ARPAnalysis(Base):
    __tablename__ = "arp_analysis"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), index=True, nullable=False)
    mac_address = Column(String(40), nullable=False)
    observation_type = Column(String(80), nullable=False)
    result = Column(Text, nullable=False)
    severity = Column(String(20), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    simulation_type = Column(String(80), index=True, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(40), default="Completed", nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    creator = relationship("User", back_populates="simulations")
