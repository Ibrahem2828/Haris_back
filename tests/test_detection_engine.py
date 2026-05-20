from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ssh_bruteforce_detection_scenario():
    client.post("/simulate/ssh-bruteforce")
    response = client.post("/detect/run-all")
    assert response.status_code == 200
    alerts = client.get("/alerts").json()
    assert any(alert["attack_type"] == "ssh_bruteforce" for alert in alerts)


def test_arp_spoofing_detection_scenario():
    client.post("/simulate/arp-spoofing")
    client.post("/detect/run-all")
    alerts = client.get("/alerts").json()
    assert any(alert["attack_type"] == "arp_spoofing" for alert in alerts)
