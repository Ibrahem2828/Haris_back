from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("incidents", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlertTimeline",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(choices=[("created", "Created"), ("status_changed", "Status Changed"), ("response_generated", "Response Generated"), ("approved", "Approved"), ("rejected", "Rejected"), ("executed", "Executed"), ("resolved", "Resolved"), ("false_positive", "False Positive"), ("closed", "Closed"), ("note", "Note")], max_length=32)),
                ("old_status", models.CharField(blank=True, max_length=32, null=True)),
                ("new_status", models.CharField(blank=True, max_length=32, null=True)),
                ("message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("alert", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="timeline", to="incidents.alert")),
            ],
            options={"ordering": ["created_at"]},
        ),
    ]
