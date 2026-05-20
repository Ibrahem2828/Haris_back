from __future__ import annotations

import hashlib
from datetime import datetime
from ipaddress import ip_address

from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive, make_aware


def parse_timestamp(value):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        dt = parse_datetime(str(value))
        if dt is None:
            raise ValueError(f"Invalid timestamp: {value}")
    return make_aware(dt) if is_naive(dt) else dt


def normalize_ip(value):
    if value in (None, ""):
        return None
    return str(ip_address(str(value).strip()))


def alert_fingerprint(attack_type, source_ip, destination_ip, first_seen, last_seen):
    raw = "|".join(
        [
            str(attack_type),
            str(source_ip),
            str(destination_ip or ""),
            first_seen.isoformat(),
            last_seen.isoformat(),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def response_success(data=None, message=None):
    payload = data or {}
    if message:
        payload["message"] = message
    return payload
