from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.audit.services import audit_log

from ..models import Alert, AlertTimeline


class IncidentWorkflow:
    transitions = {
        Alert.Statuses.NEW: {Alert.Statuses.REVIEWING},
        Alert.Statuses.REVIEWING: {Alert.Statuses.RESPONSE_SUGGESTED},
        Alert.Statuses.RESPONSE_SUGGESTED: {Alert.Statuses.WAITING_APPROVAL},
        Alert.Statuses.WAITING_APPROVAL: {Alert.Statuses.APPROVED, Alert.Statuses.REJECTED},
        Alert.Statuses.APPROVED: {Alert.Statuses.RESOLVED},
        Alert.Statuses.RESOLVED: {Alert.Statuses.CLOSED},
    }

    def start_review(self, alert, user):
        return self.transition(alert, Alert.Statuses.REVIEWING, user, "Alert review started.", "status_changed")

    def suggest_response(self, alert):
        return self.transition(alert, Alert.Statuses.RESPONSE_SUGGESTED, None, "Response suggested.", "response_generated", allow_same=True)

    def wait_for_approval(self, alert):
        return self.transition(alert, Alert.Statuses.WAITING_APPROVAL, None, "Waiting for response approval.", "status_changed")

    def approve(self, alert, user):
        return self.transition(alert, Alert.Statuses.APPROVED, user, "Response approved.", "approved", allow_same=True, allow_from={Alert.Statuses.RESPONSE_SUGGESTED})

    def reject(self, alert, user, reason=None):
        return self.transition(alert, Alert.Statuses.REJECTED, user, reason or "Response rejected.", "rejected", allow_same=True)

    def mark_resolved(self, alert, user, notes=None):
        return self.transition(alert, Alert.Statuses.RESOLVED, user, notes or "Incident resolved.", "resolved", allow_from={Alert.Statuses.APPROVED, Alert.Statuses.REVIEWING, Alert.Statuses.RESPONSE_SUGGESTED})

    def mark_false_positive(self, alert, user, notes=None):
        if alert.status == Alert.Statuses.CLOSED and not getattr(user, "is_staff_or_admin_role", False):
            raise PermissionDenied("Closed alerts can only be modified by an admin.")
        return self.transition(alert, Alert.Statuses.FALSE_POSITIVE, user, notes or "Alert marked false positive.", "false_positive", allow_any_non_closed=True)

    def close(self, alert, user, notes=None):
        return self.transition(alert, Alert.Statuses.CLOSED, user, notes or "Incident closed.", "closed", allow_from={Alert.Statuses.RESOLVED, Alert.Statuses.FALSE_POSITIVE, Alert.Statuses.REJECTED})

    def transition(self, alert, new_status, user, message, event_type, allow_same=False, allow_from=None, allow_any_non_closed=False):
        old_status = alert.status
        if old_status == Alert.Statuses.CLOSED and not getattr(user, "is_staff_or_admin_role", False):
            raise PermissionDenied("Closed alerts can only be modified by an admin.")
        allowed = allow_same and old_status == new_status
        if allow_from and old_status in allow_from:
            allowed = True
        if allow_any_non_closed and old_status != Alert.Statuses.CLOSED:
            allowed = True
        if new_status in self.transitions.get(old_status, set()):
            allowed = True
        if not allowed:
            raise ValidationError(f"Invalid incident transition from {old_status} to {new_status}.")
        alert.status = new_status
        alert.save(update_fields=["status", "updated_at"])
        self.record_timeline(alert, event_type, user, message, old_status, new_status)
        if user:
            audit_log(user, "alert_status_changed", "Alert", alert.id, metadata={"old_status": old_status, "new_status": new_status})
        return alert

    def add_note(self, alert, user, message):
        return self.record_timeline(alert, "note", user, message)

    def record_timeline(self, alert, event_type, user=None, message="", old_status=None, new_status=None):
        return AlertTimeline.objects.create(
            alert=alert,
            event_type=event_type,
            old_status=old_status,
            new_status=new_status,
            message=message,
            actor=user if getattr(user, "is_authenticated", False) else None,
        )
