from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_generate_port_scan_logs():
    response = client.post("/simulate/port-scan")
    assert response.status_code == 200
    assert response.json()["created_events"] >= 12
