from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    name: str
    username: str
    role: str = Field(..., examples=["network_admin", "security_engineer", "student"])


class UserRead(UserCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str


class EventCreate(BaseModel):
    timestamp: Optional[datetime] = None
    source_ip: str
    destination_ip: Optional[str] = None
    protocol: str = "UNKNOWN"
    port: Optional[int] = None
    event_type: str = "unknown"
    status: Optional[str] = None
    source_vlan: Optional[int] = None
    destination_vlan: Optional[int] = None
    source_mac: Optional[str] = None
    destination_mac: Optional[str] = None
    raw_message: Optional[str] = None
    is_suspicious: bool = False


class EventRead(EventCreate):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class DetectionRuleCreate(BaseModel):
    name: str
    description: str
    attack_type: str
    threshold: int
    time_window_seconds: int
    severity: str
    enabled: bool = True


class DetectionRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    attack_type: Optional[str] = None
    threshold: Optional[int] = None
    time_window_seconds: Optional[int] = None
    severity: Optional[str] = None
    enabled: Optional[bool] = None


class DetectionRuleRead(DetectionRuleCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AlertRead(BaseModel):
    id: int
    event_id: Optional[int]
    attack_type: str
    severity: str
    source_ip: str
    destination_ip: Optional[str]
    matched_rule: str
    description: str
    status: str
    recommended_action: str
    cisco_command: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertStatusUpdate(BaseModel):
    status: str


class ResponseRead(BaseModel):
    id: int
    alert_id: int
    action_type: str
    description: str
    cisco_command: str
    execution_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ARPAnalyzeRequest(BaseModel):
    event_id: Optional[int] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    observation_type: str = "arp_reply"
    is_unsolicited: bool = False


class ARPAnalysisRead(BaseModel):
    id: int
    ip_address: str
    mac_address: str
    observation_type: str
    result: str
    severity: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class SimulationRead(BaseModel):
    id: int
    simulation_type: str
    description: str
    status: str
    created_by: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DetectResponse(BaseModel):
    analyzed_events: int
    created_alerts: int
    message: str


class ImportResponse(BaseModel):
    imported_events: int
    message: str
