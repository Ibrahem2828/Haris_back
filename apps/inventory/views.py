from django_filters import rest_framework as filters
from rest_framework import viewsets

from apps.common.permissions import IsNetworkAdminOrAdmin, ReadOnlyOrAdmin

from .models import Device, Network, VLAN
from .serializers import DeviceSerializer, NetworkSerializer, VLANSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all().order_by("name")
    serializer_class = NetworkSerializer
    permission_classes = [ReadOnlyOrAdmin | IsNetworkAdminOrAdmin]
    filterset_fields = ["is_active"]
    search_fields = ["name", "cidr", "description"]
    ordering_fields = ["name", "created_at"]


class VLANViewSet(viewsets.ModelViewSet):
    queryset = VLAN.objects.select_related("network").all().order_by("vlan_id")
    serializer_class = VLANSerializer
    permission_classes = [ReadOnlyOrAdmin | IsNetworkAdminOrAdmin]
    filterset_fields = ["network", "vlan_id", "is_restricted"]
    search_fields = ["name", "purpose", "gateway_ip"]
    ordering_fields = ["vlan_id", "name", "created_at"]


class DeviceFilter(filters.FilterSet):
    class Meta:
        model = Device
        fields = ["ip_address", "device_type", "vlan", "status"]


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related("vlan", "vlan__network").all().order_by("name")
    serializer_class = DeviceSerializer
    permission_classes = [ReadOnlyOrAdmin | IsNetworkAdminOrAdmin]
    filterset_class = DeviceFilter
    search_fields = ["name", "ip_address", "mac_address", "description"]
    ordering_fields = ["name", "ip_address", "device_type", "status", "created_at"]
