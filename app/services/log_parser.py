import csv
import json
import re
from datetime import datetime
from io import StringIO

from app.schemas import EventCreate


FLOW_RE = re.compile(
    r"(?P<src>\d{1,3}(?:\.\d{1,3}){3})(?:\((?P<src_port>\d+)\))?\s*->\s*(?P<dst>\d{1,3}(?:\.\d{1,3}){3})(?:\((?P<dst_port>\d+)\))?",
    re.IGNORECASE,
)
PROTO_RE = re.compile(r"\b(tcp|udp|icmp|ssh|arp)\b", re.IGNORECASE)


def normalize_event_dict(data: dict) -> EventCreate:
    payload = dict(data)
    if isinstance(payload.get("timestamp"), str) and payload["timestamp"]:
        payload["timestamp"] = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
    if payload.get("port") in ("", None):
        payload["port"] = None
    if payload.get("source_vlan") in ("", None):
        payload["source_vlan"] = None
    if payload.get("destination_vlan") in ("", None):
        payload["destination_vlan"] = None
    payload["protocol"] = (payload.get("protocol") or "UNKNOWN").upper()
    return EventCreate(**payload)


def parse_log_line(line: str) -> EventCreate:
    protocol = "UNKNOWN"
    proto_match = PROTO_RE.search(line)
    if proto_match:
        protocol = proto_match.group(1).upper()
    source_ip = "0.0.0.0"
    destination_ip = None
    port = None
    flow = FLOW_RE.search(line)
    if flow:
        source_ip = flow.group("src")
        destination_ip = flow.group("dst")
        port = int(flow.group("dst_port")) if flow.group("dst_port") else None
    lower = line.lower()
    status = "denied" if "denied" in lower else "permitted" if "permitted" in lower else "observed"
    event_type = "icmp_packet" if protocol == "ICMP" else "arp_event" if protocol == "ARP" else "ssh_login" if port == 22 else "port_connection" if destination_ip else "unknown"
    return EventCreate(
        source_ip=source_ip,
        destination_ip=destination_ip,
        protocol=protocol,
        port=port,
        event_type=event_type,
        status=status,
        raw_message=line,
    )


def parse_imported_content(filename: str, content: bytes) -> list[EventCreate]:
    text = content.decode("utf-8-sig")
    lower_name = filename.lower()
    if lower_name.endswith(".json"):
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("events", [])
        return [normalize_event_dict(item) for item in data]
    if lower_name.endswith(".csv"):
        return [normalize_event_dict(row) for row in csv.DictReader(StringIO(text))]
    return [parse_log_line(line) for line in text.splitlines() if line.strip()]
