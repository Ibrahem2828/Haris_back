from rest_framework.routers import DefaultRouter

from .views import DeviceViewSet, NetworkViewSet, VLANViewSet


router = DefaultRouter()
router.register("networks", NetworkViewSet, basename="network")
router.register("vlans", VLANViewSet, basename="vlan")
router.register("devices", DeviceViewSet, basename="device")

urlpatterns = router.urls
