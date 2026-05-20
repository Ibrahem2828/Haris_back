from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ARPAnalyzeView, ARPSampleViewSet


router = DefaultRouter()
router.register("samples", ARPSampleViewSet, basename="arp-sample")

urlpatterns = [
    path("analyze/", ARPAnalyzeView.as_view(), name="arp-analyze"),
] + router.urls
