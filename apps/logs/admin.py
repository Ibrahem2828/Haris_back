from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "event_type", "source_ip", "destination_ip", "protocol", "port", "status")
    list_filter = ("event_type", "protocol", "status", "is_processed")
    search_fields = ("source_ip", "destination_ip", "raw_message")
