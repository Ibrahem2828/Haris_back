from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone

from apps.detection.models import DetectionJob, DetectionRule
from apps.incidents.models import Alert
from apps.inventory.models import Device, VLAN
from apps.logs.models import ActivityLog
from apps.responses.models import ResponseAction


class DashboardMetrics:
    def summary(self):
        last_alert = Alert.objects.order_by("-created_at").first()
        suspicious = self.top_suspicious_ips(limit=1)
        critical = Alert.objects.filter(severity=Alert.Severities.CRITICAL).count()
        high = Alert.objects.filter(severity=Alert.Severities.HIGH).count()
        return {
            "devices_count": Device.objects.count(),
            "vlans_count": VLAN.objects.count(),
            "logs_count": ActivityLog.objects.count(),
            "alerts_count": Alert.objects.count(),
            "critical_alerts": critical,
            "high_alerts": high,
            "last_attack": last_alert.attack_type.replace("_", " ").title() if last_alert else None,
            "most_suspicious_ip": suspicious[0]["source_ip"] if suspicious else None,
            "system_status": self._system_status(critical, high),
        }

    def recent_alerts(self, limit=10):
        return Alert.objects.select_related("rule").order_by("-created_at")[:limit]

    def recent_logs(self, limit=10):
        return ActivityLog.objects.order_by("-timestamp")[:limit]

    def attack_distribution(self):
        return list(Alert.objects.values("attack_type").annotate(count=Count("id")).order_by("-count"))

    def top_suspicious_ips(self, limit=10):
        return list(Alert.objects.values("source_ip").annotate(alerts_count=Count("id")).order_by("-alerts_count")[:limit])

    def network_map(self):
        vlans = list(VLAN.objects.values("id", "vlan_id", "name", "gateway_ip", "is_restricted"))
        devices = list(Device.objects.values("id", "name", "ip_address", "device_type", "status", "vlan_id"))
        recent_logs = ActivityLog.objects.exclude(destination_ip__isnull=True).order_by("-timestamp")[:200]
        seen = set()
        links = []
        for log in recent_logs:
            key = (log.source_ip, log.destination_ip)
            if key in seen:
                continue
            seen.add(key)
            links.append(
                {
                    "source": log.source_ip,
                    "target": log.destination_ip,
                    "protocol": log.protocol,
                    "event_type": log.event_type,
                    "last_seen": log.timestamp,
                }
            )
        return {"vlans": vlans, "devices": devices, "links": links}

    def security_posture(self):
        open_alerts = Alert.objects.exclude(status__in=[Alert.Statuses.CLOSED, Alert.Statuses.FALSE_POSITIVE, Alert.Statuses.RESOLVED])
        critical = open_alerts.filter(severity=Alert.Severities.CRITICAL).count()
        high = open_alerts.filter(severity=Alert.Severities.HIGH).count()
        vlan_24h = open_alerts.filter(attack_type="vlan_violation", created_at__gte=timezone.now() - timedelta(hours=24)).count()
        score = max(0, 100 - critical * 15 - high * 7 - vlan_24h * 5)
        reasons = []
        if critical:
            reasons.append(f"{critical} critical alerts are open")
        if high:
            reasons.append(f"{high} high alerts are open")
        if vlan_24h:
            reasons.append(f"{vlan_24h} VLAN violations detected in last 24h")
        if not reasons:
            reasons.append("No high-risk open incidents detected")
        return {"score": score, "level": self._system_status(critical, high), "reasons": reasons}

    def alerts_timeseries(self, range_value="24h"):
        now = timezone.now()
        if range_value == "7d":
            start, trunc = now - timedelta(days=7), TruncDate("created_at")
        elif range_value == "30d":
            start, trunc = now - timedelta(days=30), TruncDate("created_at")
        else:
            start, trunc = now - timedelta(hours=24), TruncHour("created_at")
        return list(Alert.objects.filter(created_at__gte=start).annotate(bucket=trunc).values("bucket").annotate(count=Count("id")).order_by("bucket"))

    def severity_breakdown(self):
        return list(Alert.objects.values("severity").annotate(count=Count("id")).order_by("severity"))

    def vlan_risk(self):
        rows = []
        for vlan in VLAN.objects.all():
            count = Alert.objects.filter(Q(evidence__source_vlan=vlan.vlan_id) | Q(evidence__destination_vlan=vlan.vlan_id)).count()
            rows.append({"vlan_id": vlan.vlan_id, "name": vlan.name, "alerts_count": count, "risk_level": self._risk_from_count(count)})
        return rows

    def device_risk(self):
        rows = []
        for device in Device.objects.all():
            count = Alert.objects.filter(Q(source_ip=device.ip_address) | Q(destination_ip=device.ip_address)).count()
            rows.append({"device_id": device.id, "name": device.name, "ip_address": device.ip_address, "alerts_count": count, "status": device.status, "risk_level": self._risk_from_count(count)})
        return sorted(rows, key=lambda item: item["alerts_count"], reverse=True)

    def detection_health(self):
        last_job = DetectionJob.objects.order_by("-created_at").first()
        return {
            "rules_count": DetectionRule.objects.count(),
            "active_rules": DetectionRule.objects.filter(is_active=True).count(),
            "last_detection_run": last_job.finished_at if last_job else None,
            "last_job_status": last_job.status if last_job else None,
            "logs_unprocessed": ActivityLog.objects.filter(is_processed=False).count(),
        }

    def incident_status_breakdown(self):
        return list(Alert.objects.values("status").annotate(count=Count("id")).order_by("status"))

    def response_status_breakdown(self):
        return list(ResponseAction.objects.values("approval_status").annotate(count=Count("id")).order_by("approval_status"))

    @staticmethod
    def _system_status(critical, high):
        if critical:
            return "critical"
        if high:
            return "warning"
        return "normal"

    @staticmethod
    def _risk_from_count(count):
        if count >= 5:
            return "high"
        if count >= 1:
            return "medium"
        return "low"
