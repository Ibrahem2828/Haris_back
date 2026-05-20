from rest_framework import serializers

from .models import ARPSample


class ARPSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARPSample
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
