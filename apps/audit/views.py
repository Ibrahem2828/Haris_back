from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogFilter(filters.FilterSet):
    created_at_after = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = AuditLog
        fields = ["actor", "action", "resource_type"]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AuditLogFilter
    ordering_fields = ["created_at", "action", "resource_type"]
    search_fields = ["action", "resource_type", "resource_id"]
