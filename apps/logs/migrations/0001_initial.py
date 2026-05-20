from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("timestamp", models.DateTimeField(db_index=True)),
                ("source_ip", models.GenericIPAddressField(db_index=True)),
                ("destination_ip", models.GenericIPAddressField(blank=True, db_index=True, null=True)),
                ("source_vlan", models.IntegerField(blank=True, db_index=True, null=True)),
                ("destination_vlan", models.IntegerField(blank=True, db_index=True, null=True)),
                ("protocol", models.CharField(blank=True, db_index=True, max_length=32)),
                ("port", models.PositiveIntegerField(blank=True, null=True)),
                ("action", models.CharField(blank=True, max_length=64)),
                ("status", models.CharField(blank=True, db_index=True, max_length=64)),
                ("event_type", models.CharField(choices=[("ssh_login", "SSH Login"), ("port_connection", "Port Connection"), ("icmp_packet", "ICMP Packet"), ("vlan_traffic", "VLAN Traffic"), ("arp_event", "ARP Event"), ("unknown", "Unknown")], db_index=True, default="unknown", max_length=32)),
                ("raw_message", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_processed", models.BooleanField(default=False)),
            ],
            options={"ordering": ["-timestamp"]},
        ),
        migrations.AddIndex(model_name="activitylog", index=models.Index(fields=["event_type", "timestamp"], name="logs_activi_event_t_dc7e36_idx")),
        migrations.AddIndex(model_name="activitylog", index=models.Index(fields=["source_ip", "timestamp"], name="logs_activi_source__1d0e60_idx")),
    ]
