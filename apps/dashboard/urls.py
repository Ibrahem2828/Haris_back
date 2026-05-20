from django.urls import path

from .views import (
    AttackDistributionView,
    AlertsTimeseriesView,
    DetectionHealthView,
    DeviceRiskView,
    IncidentStatusBreakdownView,
    NetworkMapView,
    RecentAlertsView,
    RecentLogsView,
    ResponseStatusBreakdownView,
    SecurityPostureView,
    SeverityBreakdownView,
    SummaryView,
    TopSuspiciousIPsView,
    VLANRiskView,
)


urlpatterns = [
    path("summary/", SummaryView.as_view(), name="dashboard-summary"),
    path("recent-alerts/", RecentAlertsView.as_view(), name="dashboard-recent-alerts"),
    path("recent-logs/", RecentLogsView.as_view(), name="dashboard-recent-logs"),
    path("attack-distribution/", AttackDistributionView.as_view(), name="dashboard-attack-distribution"),
    path("top-suspicious-ips/", TopSuspiciousIPsView.as_view(), name="dashboard-top-suspicious-ips"),
    path("network-map/", NetworkMapView.as_view(), name="dashboard-network-map"),
    path("security-posture/", SecurityPostureView.as_view(), name="dashboard-security-posture"),
    path("alerts-timeseries/", AlertsTimeseriesView.as_view(), name="dashboard-alerts-timeseries"),
    path("severity-breakdown/", SeverityBreakdownView.as_view(), name="dashboard-severity-breakdown"),
    path("vlan-risk/", VLANRiskView.as_view(), name="dashboard-vlan-risk"),
    path("device-risk/", DeviceRiskView.as_view(), name="dashboard-device-risk"),
    path("detection-health/", DetectionHealthView.as_view(), name="dashboard-detection-health"),
    path("incident-status-breakdown/", IncidentStatusBreakdownView.as_view(), name="dashboard-incident-status-breakdown"),
    path("response-status-breakdown/", ResponseStatusBreakdownView.as_view(), name="dashboard-response-status-breakdown"),
]
