from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Network",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("cidr", models.CharField(max_length=64)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="VLAN",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("vlan_id", models.PositiveIntegerField()),
                ("name", models.CharField(max_length=120)),
                ("gateway_ip", models.GenericIPAddressField()),
                ("purpose", models.CharField(blank=True, max_length=255)),
                ("is_restricted", models.BooleanField(default=False)),
                ("network", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vlans", to="inventory.network")),
            ],
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("ip_address", models.GenericIPAddressField(db_index=True)),
                ("mac_address", models.CharField(blank=True, max_length=32)),
                ("device_type", models.CharField(choices=[("router", "Router"), ("switch", "Switch"), ("server", "Server"), ("pc", "PC"), ("laptop", "Laptop"), ("attacker", "Attacker"), ("security_server", "Security Server"), ("syslog_server", "Syslog Server"), ("unknown", "Unknown")], default="unknown", max_length=32)),
                ("status", models.CharField(choices=[("active", "Active"), ("inactive", "Inactive"), ("suspicious", "Suspicious"), ("under_attack", "Under Attack"), ("unknown", "Unknown")], default="unknown", max_length=32)),
                ("description", models.TextField(blank=True)),
                ("vlan", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="devices", to="inventory.vlan")),
            ],
        ),
        migrations.AddConstraint(
            model_name="vlan",
            constraint=models.UniqueConstraint(fields=("network", "vlan_id"), name="unique_vlan_per_network"),
        ),
    ]
