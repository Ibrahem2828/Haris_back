from __future__ import annotations

import csv
import io
import json
import re
from typing import Iterable

from django.utils import timezone

from apps.common.utils import parse_timestamp


CSV_COLUMNS = [
    "timestamp",
    "source_ip",
    "destination_ip",
    "source_vlan",
    "destination_vlan",
    "protocol",
    "port",
    "event_type",
    "action",
    "status",
    "raw_message",
]


def _validate_upload_extension(uploaded_file, allowed_extensions: set[str], label: str) -> None:
    name = getattr(uploaded_file, "name", "") or ""
    if not any(name.lower().endswith(extension) for extension in allowed_extensions):
        raise ValueError(f"Upload a valid {label} file.")


def _nullable_int(value):
    if value in (None, ""):
        return None
    return int(value)


def normalize_log_payload(payload: dict) -> dict:
    data = dict(payload)
    data["timestamp"] = parse_timestamp(data.get("timestamp"))
    data["destination_ip"] = data.get("destination_ip") or None
    data["source_vlan"] = _nullable_int(data.get("source_vlan"))
    data["destination_vlan"] = _nullable_int(data.get("destination_vlan"))
    data["port"] = _nullable_int(data.get("port"))
    data["protocol"] = (data.get("protocol") or "").upper()
    data["metadata"] = data.get("metadata") or {}
    return data


def parse_csv_upload(uploaded_file) -> list[dict]:
    _validate_upload_extension(uploaded_file, {".csv"}, "CSV")
    content = uploaded_file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    missing = [column for column in CSV_COLUMNS if column not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(f"Missing CSV columns: {', '.join(missing)}")
    return [normalize_log_payload(row) for row in reader]


def parse_json_upload(uploaded_file=None, payload=None) -> list[dict]:
    if uploaded_file is not None:
        _validate_upload_extension(uploaded_file, {".json"}, "JSON")
        raw = uploaded_file.read().decode("utf-8")
        data = json.loads(raw)
    else:
        data = payload
    if isinstance(data, dict) and "logs" in data:
        data = data["logs"]
    if not isinstance(data, Iterable) or isinstance(data, (str, bytes, dict)):
        raise ValueError("JSON upload must be a list of logs or an object with a 'logs' list.")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError("Each JSON log entry must be an object.")
    return [normalize_log_payload(item) for item in data]


SYSLOG_IP_RE = re.compile(r"(?P<src>\d{1,3}(?:\.\d{1,3}){3})(?:\((?P<src_port>\d+)\))?\s*->\s*(?P<dst>\d{1,3}(?:\.\d{1,3}){3})(?:\((?P<dst_port>\d+)\))?", re.IGNORECASE)
SYSLOG_PROTO_RE = re.compile(r"\b(tcp|udp|icmp|ssh|arp)\b", re.IGNORECASE)


def parse_syslog_message(message: str, source_device: str = "") -> dict:
    now = timezone.now()
    data = {
        "timestamp": now,
        "source_ip": "0.0.0.0",
        "destination_ip": None,
        "protocol": "",
        "port": None,
        "event_type": "unknown",
        "action": "",
        "status": "",
        "raw_message": message,
        "metadata": {"source_device": source_device} if source_device else {},
    }
    ip_match = SYSLOG_IP_RE.search(message or "")
    if ip_match:
        data["source_ip"] = ip_match.group("src")
        data["destination_ip"] = ip_match.group("dst")
        data["port"] = int(ip_match.group("dst_port")) if ip_match.group("dst_port") else None
    proto_match = SYSLOG_PROTO_RE.search(message or "")
    if proto_match:
        data["protocol"] = proto_match.group(1).upper()
    lower = (message or "").lower()
    if "denied" in lower or "deny" in lower:
        data["action"] = "denied"
        data["status"] = "denied"
    elif "permitted" in lower or "permit" in lower:
        data["action"] = "permitted"
        data["status"] = "permitted"
    if data["protocol"] == "ICMP":
        data["event_type"] = "icmp_packet"
    elif data["protocol"] == "ARP":
        data["event_type"] = "arp_event"
    elif data["port"] == 22 or data["protocol"] == "SSH":
        data["event_type"] = "ssh_login"
    elif data["source_ip"] != "0.0.0.0" and data["destination_ip"]:
        data["event_type"] = "port_connection"
    return data
