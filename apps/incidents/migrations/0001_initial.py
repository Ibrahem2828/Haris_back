from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("detection", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Alert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("attack_type", models.CharField(db_index=True, max_length=64)),
                ("source_ip", models.GenericIPAddressField(db_index=True)),
                ("destination_ip", models.GenericIPAddressField(blank=True, db_index=True, null=True)),
                ("severity", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], db_index=True, max_length=16)),
                ("status", models.CharField(choices=[("new", "New"), ("reviewing", "Reviewing"), ("response_suggested", "Response Suggested"), ("waiting_approval", "Waiting Approval"), ("approved", "Approved"), ("rejected", "Rejected"), ("resolved", "Resolved"), ("false_positive", "False Positive"), ("closed", "Closed")], db_index=True, default="new", max_length=32)),
                ("description", models.TextField()),
                ("evidence", models.JSONField(blank=True, default=dict)),
                ("first_seen", models.DateTimeField(db_index=True)),
                ("last_seen", models.DateTimeField(db_index=True)),
                ("rule", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="alerts", to="detection.detectionrule")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="alert", index=models.Index(fields=["attack_type", "source_ip", "created_at"], name="incidents_a_attack__a020c7_idx")),
    ]
