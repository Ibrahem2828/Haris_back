from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ARPSample",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField()),
                ("ip_address", models.GenericIPAddressField(db_index=True)),
                ("mac_address", models.CharField(max_length=32)),
                ("arp_type", models.CharField(choices=[("request", "Request"), ("reply", "Reply")], max_length=16)),
                ("is_unsolicited", models.BooleanField(default=False)),
                ("source_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("raw_data", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-timestamp"]},
        ),
    ]
