from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.incidents.models import Alert
from apps.logs.models import ActivityLog
from apps.responses.models import ResponseAction


class Command(BaseCommand):
    help = "Reset demo logs, demo alerts, and demo responses, then recreate demo data."

    def handle(self, *args, **options):
        demo_alerts = Alert.objects.filter(evidence__is_demo=True)
        ResponseAction.objects.filter(alert__in=demo_alerts).delete()
        deleted_alerts, _ = demo_alerts.delete()
        deleted_logs, _ = ActivityLog.objects.filter(metadata__is_demo=True).delete()
        call_command("seed_demo_data")
        self.stdout.write(self.style.SUCCESS(f"Demo reset complete. deleted_logs={deleted_logs}, deleted_alerts={deleted_alerts}"))
