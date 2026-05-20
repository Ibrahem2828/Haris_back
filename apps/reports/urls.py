from django.urls import path

from .views import AlertsCSVView, IncidentsSummaryView, LogsCSVView, SecurityReportView


urlpatterns = [
    path("alerts.csv", AlertsCSVView.as_view(), name="reports-alerts-csv"),
    path("logs.csv", LogsCSVView.as_view(), name="reports-logs-csv"),
    path("incidents-summary.json", IncidentsSummaryView.as_view(), name="reports-incidents-summary"),
    path("security-report/", SecurityReportView.as_view(), name="reports-security-report"),
]
