from rest_framework import serializers

from .models import Device, Network, VLAN


class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = "__all__"


class VLANSerializer(serializers.ModelSerializer):
    class Meta:
        model = VLAN
        fields = "__all__"


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
