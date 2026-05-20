from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DetectionJobViewSet, DetectionRuleViewSet, DetectionRunView, DetectionSchedulePreviewView


router = DefaultRouter()
router.register("rules", DetectionRuleViewSet, basename="detection-rule")
router.register("jobs", DetectionJobViewSet, basename="detection-job")

urlpatterns = [
    path("run/", DetectionRunView.as_view(), name="detection-run"),
    path("schedule-preview/", DetectionSchedulePreviewView.as_view(), name="detection-schedule-preview"),
] + router.urls
