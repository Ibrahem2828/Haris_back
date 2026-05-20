from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_and_dashboard_summary():
    assert client.get("/health").status_code == 200
    summary = client.get("/dashboard/summary")
    assert summary.status_code == 200
    assert "total_events" in summary.json()


def test_create_event_and_detect_single_event():
    event = client.post(
        "/events",
        json={
            "source_ip": "192.168.20.25",
            "destination_ip": "192.168.30.20",
            "protocol": "TCP",
            "port": 445,
            "event_type": "vlan_traffic",
            "status": "unauthorized",
            "source_vlan": 20,
            "destination_vlan": 30,
        },
    )
    assert event.status_code == 200
    event_id = event.json()["id"]
    detection = client.post(f"/detect/event/{event_id}")
    assert detection.status_code == 200
    assert detection.json()["created_or_matched_alerts"] >= 1


def test_alert_status_update_and_response_approval():
    client.post("/simulate/port-scan")
    client.post("/detect/run-all")
    alerts = client.get("/alerts").json()
    assert alerts
    alert_id = alerts[0]["id"]
    status_response = client.patch(f"/alerts/{alert_id}/status", json={"status": "Reviewed"})
    assert status_response.status_code == 200

    responses = client.get("/responses").json()
    assert responses
    response_id = responses[0]["id"]
    approval = client.patch(f"/responses/{response_id}/approve")
    assert approval.status_code == 200
    assert approval.json()["execution_status"] == "Approved"


def test_reports_rules_endpoint():
    response = client.get("/reports/rules")
    assert response.status_code == 200
    assert len(response.json()) >= 5
