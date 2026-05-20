from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.incidents.models import Alert
from apps.incidents.services.workflow import IncidentWorkflow

from .services.generator import ResponseGenerator


@receiver(post_save, sender=Alert)
def create_response_action_for_alert(sender, instance, created, **kwargs):
    if created:
        workflow = IncidentWorkflow()
        workflow.record_timeline(instance, "created", None, "Alert created by detection engine.", None, instance.status)
        ResponseGenerator().generate_for_alert(instance)
        workflow.record_timeline(instance, "response_generated", None, "Response action generated automatically.")
