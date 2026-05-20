from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("incidents", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResponseAction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("action_type", models.CharField(choices=[("block_ip", "Block IP"), ("rate_limit", "Rate Limit"), ("enhance_acl", "Enhance ACL"), ("shutdown_port", "Shutdown Port"), ("investigate", "Investigate"), ("monitor_only", "Monitor Only"), ("isolate_vlan", "Isolate VLAN"), ("bind_ip_mac", "Bind IP/MAC")], max_length=32)),
                ("title", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True)),
                ("recommended_action", models.TextField()),
                ("cisco_ios_commands", models.JSONField(blank=True, default=list)),
                ("command_text", models.TextField(blank=True)),
                ("risk_level", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium", max_length=16)),
                ("requires_approval", models.BooleanField(default=True)),
                ("approval_status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("postponed", "Postponed"), ("not_required", "Not Required")], default="pending", max_length=16)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("rejected_reason", models.TextField(blank=True)),
                ("executed", models.BooleanField(default=False)),
                ("executed_at", models.DateTimeField(blank=True, null=True)),
                ("execution_notes", models.TextField(blank=True)),
                ("alert", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="response_action", to="incidents.alert")),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_response_actions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
