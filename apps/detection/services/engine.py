from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from apps.audit.services import audit_log
from apps.common.utils import alert_fingerprint
from apps.incidents.models import Alert
from apps.logs.models import ActivityLog

from ..models import DetectionJob, DetectionRule


RESPONSE_SUGGESTIONS = {
    "ssh_bruteforce": "block_ip",
    "port_scan": "block_ip_or_monitor",
    "icmp_flood": "rate_limit_or_block",
    "vlan_violation": "review_acl",
    "arp_spoofing": "investigate_ip_mac_binding",
}


class DetectionEngine:
    def run_detection(self, from_timestamp=None, to_timestamp=None, rule_types=None, job=None, triggered_by=None, mode=DetectionJob.Modes.SYNC) -> DetectionJob:
        requested = list(rule_types or [])
        if job is None:
            job = DetectionJob.objects.create(
                status=DetectionJob.Statuses.PENDING,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                rules_requested=requested,
                triggered_by=triggered_by if getattr(triggered_by, "is_authenticated", False) else None,
                mode=mode,
            )
        try:
            job.status = DetectionJob.Statuses.RUNNING
            job.started_at = timezone.now()
            job.save(update_fields=["status", "started_at", "updated_at"])

            logs = ActivityLog.objects.all().order_by("timestamp")
            if from_timestamp:
                logs = logs.filter(timestamp__gte=from_timestamp)
            if to_timestamp:
                logs = logs.filter(timestamp__lte=to_timestamp)

            rules = DetectionRule.objects.filter(is_active=True)
            if requested:
                rules = rules.filter(rule_type__in=requested)

            alerts = []
            for rule in rules.order_by("rule_type"):
                detector = getattr(self, f"detect_{rule.rule_type}", None)
                if detector:
                    alerts.extend(detector(rule, logs))

            ActivityLog.objects.filter(pk__in=logs.values_list("pk", flat=True)).update(is_processed=True)
            job.status = DetectionJob.Statuses.COMPLETED
            job.finished_at = timezone.now()
            job.logs_processed = logs.count()
            job.alerts_created = len(alerts)
            job.save()
            if triggered_by:
                audit_log(triggered_by, "detection_run", "DetectionJob", job.id, metadata={"mode": job.mode, "rules": requested})
        except Exception as exc:  # pragma: no cover - defensive job bookkeeping
            job.status = DetectionJob.Statuses.FAILED
            job.finished_at = timezone.now()
            job.error_message = str(exc)
            job.save()
        return job

    def detect_ssh_bruteforce(self, rule, logs_queryset) -> list[Alert]:
        logs = list(
            logs_queryset.filter(
                event_type=ActivityLog.EventTypes.SSH_LOGIN,
                port=22,
                status__iexact="failed",
            )
            .filter(Q(protocol__iexact="TCP") | Q(protocol__iexact="SSH"))
            .order_by("source_ip", "timestamp")
        )
        grouped = defaultdict(list)
        for log in logs:
            grouped[log.source_ip].append(log)
        alerts = []
        for source_ip, source_logs in grouped.items():
            alerts.extend(
                self._create_threshold_window_alerts(
                    rule=rule,
                    logs=source_logs,
                    attack_type=rule.rule_type,
                    source_ip=source_ip,
                    destination_ip=None,
                    description=f"SSH brute force detected from {source_ip}.",
                    evidence_builder=lambda window: {"attempts": len(window), "log_ids": [item.id for item in window]},
                )
            )
        return alerts

    def detect_port_scan(self, rule, logs_queryset) -> list[Alert]:
        logs = list(
            logs_queryset.filter(event_type=ActivityLog.EventTypes.PORT_CONNECTION)
            .exclude(destination_ip__isnull=True)
            .exclude(port__isnull=True)
            .order_by("source_ip", "destination_ip", "timestamp")
        )
        grouped = defaultdict(list)
        for log in logs:
            grouped[(log.source_ip, log.destination_ip)].append(log)
        alerts = []
        for (source_ip, destination_ip), source_logs in grouped.items():
            window = []
            for log in source_logs:
                window = [item for item in window if log.timestamp - item.timestamp <= timedelta(seconds=rule.time_window_seconds)]
                window.append(log)
                ports = sorted({item.port for item in window if item.port is not None})
                if len(ports) > rule.threshold:
                    alert = self._create_alert(
                        rule,
                        rule.rule_type,
                        source_ip,
                        destination_ip,
                        window[0].timestamp,
                        window[-1].timestamp,
                        f"Port scan detected from {source_ip} to {destination_ip}.",
                        {"distinct_ports": len(ports), "ports": ports, "log_ids": [item.id for item in window]},
                    )
                    if alert:
                        alerts.append(alert)
                    window = []
        return alerts

    def detect_icmp_flood(self, rule, logs_queryset) -> list[Alert]:
        logs = list(
            logs_queryset.filter(Q(protocol__iexact="ICMP") | Q(event_type=ActivityLog.EventTypes.ICMP_PACKET))
            .order_by("source_ip", "timestamp")
        )
        grouped = defaultdict(list)
        for log in logs:
            grouped[log.source_ip].append(log)
        alerts = []
        for source_ip, source_logs in grouped.items():
            alerts.extend(
                self._create_threshold_window_alerts(
                    rule=rule,
                    logs=source_logs,
                    attack_type=rule.rule_type,
                    source_ip=source_ip,
                    destination_ip=None,
                    description=f"ICMP flood detected from {source_ip}.",
                    evidence_builder=lambda window: {"packets": len(window), "log_ids": [item.id for item in window]},
                )
            )
        return alerts

    def detect_vlan_violation(self, rule, logs_queryset) -> list[Alert]:
        blocked_pairs = rule.parameters.get("blocked_pairs", [])
        alerts = []
        for pair in blocked_pairs:
            matching_logs = logs_queryset.filter(
                event_type=ActivityLog.EventTypes.VLAN_TRAFFIC,
                source_vlan=pair.get("source_vlan"),
                destination_vlan=pair.get("destination_vlan"),
            ).order_by("timestamp")
            for log in matching_logs:
                alert = self._create_alert(
                    rule,
                    rule.rule_type,
                    log.source_ip,
                    log.destination_ip,
                    log.timestamp,
                    log.timestamp,
                    f"Blocked VLAN traffic detected: VLAN {log.source_vlan} to VLAN {log.destination_vlan}.",
                    {
                        "source_vlan": log.source_vlan,
                        "destination_vlan": log.destination_vlan,
                        "log_id": log.id,
                    },
                )
                if alert:
                    alerts.append(alert)
        return alerts

    def detect_arp_spoofing(self, rule, logs_queryset) -> list[Alert]:
        logs = list(logs_queryset.filter(event_type=ActivityLog.EventTypes.ARP_EVENT).order_by("timestamp"))
        alerts = []
        grouped = defaultdict(list)
        for log in logs:
            ip = log.metadata.get("ip_address")
            mac = log.metadata.get("mac_address")
            if log.metadata.get("is_unsolicited_reply") is True:
                alert = self._create_alert(
                    rule,
                    rule.rule_type,
                    log.source_ip,
                    None,
                    log.timestamp,
                    log.timestamp,
                    f"Unsolicited ARP reply detected for {ip or log.source_ip}.",
                    {"ip_address": ip, "mac_address": mac, "log_id": log.id, "reason": "unsolicited_reply"},
                )
                if alert:
                    alerts.append(alert)
            if ip and mac:
                grouped[ip].append(log)

        for ip, ip_logs in grouped.items():
            window = []
            for log in ip_logs:
                window = [item for item in window if log.timestamp - item.timestamp <= timedelta(seconds=rule.time_window_seconds)]
                window.append(log)
                macs = sorted({item.metadata.get("mac_address") for item in window if item.metadata.get("mac_address")})
                if len(macs) > 1:
                    alert = self._create_alert(
                        rule,
                        rule.rule_type,
                        log.source_ip,
                        None,
                        window[0].timestamp,
                        window[-1].timestamp,
                        f"ARP spoofing indicator detected for IP {ip}.",
                        {"ip_address": ip, "mac_addresses": macs, "log_ids": [item.id for item in window]},
                    )
                    if alert:
                        alerts.append(alert)
                    window = []
        return alerts

    def _create_threshold_window_alerts(self, rule, logs, attack_type, source_ip, destination_ip, description, evidence_builder):
        alerts = []
        window = []
        for log in logs:
            window = [item for item in window if log.timestamp - item.timestamp <= timedelta(seconds=rule.time_window_seconds)]
            window.append(log)
            if len(window) > rule.threshold:
                alert = self._create_alert(
                    rule,
                    attack_type,
                    source_ip,
                    destination_ip,
                    window[0].timestamp,
                    window[-1].timestamp,
                    description,
                    evidence_builder(window),
                )
                if alert:
                    alerts.append(alert)
                window = []
        return alerts

    def _create_alert(self, rule, attack_type, source_ip, destination_ip, first_seen, last_seen, description, evidence):
        fingerprint = alert_fingerprint(attack_type, source_ip, destination_ip, first_seen, last_seen)
        if Alert.objects.filter(evidence__fingerprint=fingerprint).exists():
            return None
        evidence = dict(evidence)
        evidence["fingerprint"] = fingerprint
        evidence["suggested_response"] = {
            "action": RESPONSE_SUGGESTIONS.get(attack_type, "review"),
            "execute_automatically": False,
        }
        return Alert.objects.create(
            rule=rule,
            attack_type=attack_type,
            source_ip=source_ip,
            destination_ip=destination_ip,
            severity=rule.severity,
            status=Alert.Statuses.RESPONSE_SUGGESTED,
            description=description,
            evidence=evidence,
            first_seen=first_seen,
            last_seen=last_seen,
        )
