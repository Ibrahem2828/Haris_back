from django.contrib import admin

from .models import ResponseAction


@admin.register(ResponseAction)
class ResponseActionAdmin(admin.ModelAdmin):
    list_display = ("title", "action_type", "risk_level", "approval_status", "executed", "created_at")
    list_filter = ("action_type", "risk_level", "approval_status", "executed")
    search_fields = ("title", "recommended_action", "alert__source_ip")
