from django.urls import path

from .views import (
    GenerateARPSpoofingView,
    GenerateICMPFloodView,
    GenerateMixedView,
    GeneratePortScanView,
    GenerateSSHBruteforceView,
    GenerateVLANViolationView,
)


urlpatterns = [
    path("generate/ssh-bruteforce/", GenerateSSHBruteforceView.as_view(), name="generate-ssh-bruteforce"),
    path("generate/port-scan/", GeneratePortScanView.as_view(), name="generate-port-scan"),
    path("generate/icmp-flood/", GenerateICMPFloodView.as_view(), name="generate-icmp-flood"),
    path("generate/vlan-violation/", GenerateVLANViolationView.as_view(), name="generate-vlan-violation"),
    path("generate/arp-spoofing/", GenerateARPSpoofingView.as_view(), name="generate-arp-spoofing"),
    path("generate/mixed/", GenerateMixedView.as_view(), name="generate-mixed"),
]
