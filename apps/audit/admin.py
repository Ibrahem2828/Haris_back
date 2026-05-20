from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "resource_type", "resource_id", "ip_address")
    list_filter = ("action", "resource_type")
    search_fields = ("resource_id", "metadata")
