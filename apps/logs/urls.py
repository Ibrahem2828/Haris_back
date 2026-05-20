from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ActivityLogViewSet, BulkActivityLogView, BulkSyslogIngestView, CSVUploadView, JSONUploadView, SyslogIngestView, clear_logs


router = DefaultRouter()
router.register("activity", ActivityLogViewSet, basename="activity-log")

urlpatterns = [
    path("bulk/", BulkActivityLogView.as_view(), name="logs-bulk"),
    path("upload/csv/", CSVUploadView.as_view(), name="logs-upload-csv"),
    path("upload/json/", JSONUploadView.as_view(), name="logs-upload-json"),
    path("syslog/", SyslogIngestView.as_view(), name="logs-syslog"),
    path("syslog/bulk/", BulkSyslogIngestView.as_view(), name="logs-syslog-bulk"),
    path("clear/", clear_logs, name="logs-clear"),
] + router.urls
