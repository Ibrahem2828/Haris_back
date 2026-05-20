from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("detection", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="detectionjob",
            name="celery_task_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="detectionjob",
            name="mode",
            field=models.CharField(choices=[("sync", "Sync"), ("async", "Async"), ("scheduled", "Scheduled"), ("simulator", "Simulator")], default="sync", max_length=16),
        ),
        migrations.AddField(
            model_name="detectionjob",
            name="triggered_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="detection_jobs", to=settings.AUTH_USER_MODEL),
        ),
    ]
