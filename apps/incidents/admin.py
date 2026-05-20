from django.contrib import admin

from .models import Alert, AlertTimeline


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("attack_type", "source_ip", "destination_ip", "severity", "status", "first_seen", "last_seen")
    list_filter = ("attack_type", "severity", "status")
    search_fields = ("source_ip", "destination_ip", "description")


@admin.register(AlertTimeline)
class AlertTimelineAdmin(admin.ModelAdmin):
    list_display = ("created_at", "alert", "event_type", "old_status", "new_status", "actor")
    list_filter = ("event_type",)
