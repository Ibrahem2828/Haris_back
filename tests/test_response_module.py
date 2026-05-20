from app.services.response_module import ResponseModule


class AlertLike:
    attack_type = "icmp_flood"
    source_ip = "192.168.20.50"
    destination_ip = "192.168.30.10"


def test_response_module_generates_cisco_command():
    data = ResponseModule().generate_response(AlertLike())
    assert "access-list 102 deny icmp host 192.168.20.50 any" in data["cisco_command"]
    assert "suggested response" not in data["recommended_action"].lower()
