from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DetectionJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")], default="pending", max_length=16)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("from_timestamp", models.DateTimeField(blank=True, null=True)),
                ("to_timestamp", models.DateTimeField(blank=True, null=True)),
                ("rules_requested", models.JSONField(blank=True, default=list)),
                ("logs_processed", models.PositiveIntegerField(default=0)),
                ("alerts_created", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="DetectionRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("rule_type", models.CharField(choices=[("ssh_bruteforce", "SSH Brute Force"), ("port_scan", "Port Scan"), ("icmp_flood", "ICMP Flood"), ("vlan_violation", "VLAN Violation"), ("arp_spoofing", "ARP Spoofing")], max_length=32, unique=True)),
                ("description", models.TextField(blank=True)),
                ("threshold", models.PositiveIntegerField()),
                ("time_window_seconds", models.PositiveIntegerField()),
                ("severity", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], max_length=16)),
                ("is_active", models.BooleanField(default=True)),
                ("parameters", models.JSONField(blank=True, default=dict)),
            ],
        ),
    ]
