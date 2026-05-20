# Haris Frontend Integration Guide

Use `VITE_API_BASE_URL` for the backend origin, for example `https://api.example.com`.

## Authentication

Log in with:

```http
POST /api/auth/login/
Content-Type: application/json

{"username": "admin", "password": "change-me"}
```

The response contains `access` and `refresh`. Store tokens in a secure frontend auth store. Prefer memory plus refresh-token persistence appropriate to the frontend threat model. Avoid exposing tokens in URLs or logs.

Authenticated requests use:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

Refresh expired access tokens with:

```http
POST /api/auth/refresh/
{"refresh": "<refresh_token>"}
```

Load the current user and role with `GET /api/auth/me/`.

## Logs

Create a single activity log with `POST /api/logs/activity/`.

Upload JSON logs with:

```http
POST /api/logs/upload/json/
Content-Type: application/json

{"logs": [{"timestamp": "2026-05-01T10:00:00Z", "source_ip": "192.168.20.15", "destination_ip": "192.168.30.10", "protocol": "TCP", "port": 22, "event_type": "ssh_login", "status": "failed"}]}
```

Upload CSV logs with multipart form field `file`:

```http
POST /api/logs/upload/csv/
Content-Type: multipart/form-data
```

Required CSV columns are `timestamp`, `source_ip`, `destination_ip`, `source_vlan`, `destination_vlan`, `protocol`, `port`, `event_type`, `action`, `status`, and `raw_message`.

Syslog-like ingestion is available at `POST /api/logs/syslog/` and `POST /api/logs/syslog/bulk/`.

## Detection

Run detection with:

```http
POST /api/detection/run/

{"from": "2026-05-01T10:00:00Z", "to": "2026-05-01T11:00:00Z", "rules": ["port_scan"], "async": false}
```

Set `"async": true` to queue a Celery-backed job when Redis/Celery is configured. Poll `GET /api/detection/jobs/{id}/` for status.

## Dashboard

Use `GET /api/dashboard/summary/` for the top-level dashboard. Supplement it with:

- `GET /api/dashboard/recent-alerts/`
- `GET /api/dashboard/recent-logs/`
- `GET /api/dashboard/security-posture/`
- `GET /api/dashboard/network-map/`
- `GET /api/dashboard/alerts-timeseries/?range=24h`
- `GET /api/dashboard/severity-breakdown/`

## Alerts

List alerts with `GET /api/incidents/alerts/`. Use filters such as `severity`, `status`, `attack_type`, `source_ip`, `destination_ip`, `created_at_after`, and `created_at_before`.

Alert detail is `GET /api/incidents/alerts/{id}/`. Timeline is `GET /api/incidents/alerts/{id}/timeline/`.

Workflow actions:

- `POST /api/incidents/alerts/{id}/start-review/`
- `POST /api/incidents/alerts/{id}/suggest-response/`
- `POST /api/incidents/alerts/{id}/mark-resolved/`
- `POST /api/incidents/alerts/{id}/mark-false-positive/`
- `POST /api/incidents/alerts/{id}/close/`
- `POST /api/incidents/alerts/{id}/add-note/`

## Response Actions

List suggested response actions with `GET /api/responses/actions/`. Approve or reject with:

```http
POST /api/responses/actions/{id}/approve/
POST /api/responses/actions/{id}/reject/
POST /api/responses/actions/{id}/postpone/
POST /api/responses/actions/{id}/mark-executed/
```

Approval endpoints require `ADMIN` or `NETWORK_ADMIN`.

Use `POST /api/responses/generate-preview/` to preview Cisco IOS command suggestions before an alert-backed response exists.

## ARP Analysis

Create ARP samples with `POST /api/arp/samples/`. Analyze all samples or selected samples with:

```http
POST /api/arp/analyze/

{"sample_ids": [1, 2, 3]}
```

The backend converts samples into activity logs and runs ARP spoofing detection.

## Reports

Exports:

- `GET /api/reports/alerts.csv`
- `GET /api/reports/logs.csv`
- `GET /api/reports/incidents-summary.json`
- `GET /api/reports/security-report/`

CSV endpoints return `text/csv` with attachment filenames. JSON endpoints can be rendered directly in reporting screens.

## Suggested Pages

- Dashboard
- Network Map
- Activity Logs
- Alerts
- Alert Details
- Response Actions
- ARP Analysis
- Reports
- Audit Logs
- Settings

## API Docs

Swagger UI is available at `/docs/`. The OpenAPI schema is available at `/schema/`.
