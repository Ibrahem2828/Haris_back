from app.core.constants import (
    ATTACK_ARP_SPOOFING,
    ATTACK_ICMP_FLOOD,
    ATTACK_PORT_SCAN,
    ATTACK_SSH_BRUTE_FORCE,
    ATTACK_VLAN_VIOLATION,
)
from app.utils import cisco_templates


class ResponseModule:
    def get_action_by_attack_type(self, attack_type: str) -> str:
        actions = {
            ATTACK_SSH_BRUTE_FORCE: "Block attacker source IP",
            ATTACK_PORT_SCAN: "Block source IP or escalate monitoring",
            ATTACK_ICMP_FLOOD: "Block ICMP from source or apply rate limiting",
            ATTACK_VLAN_VIOLATION: "Enhance ACL between VLANs",
            ATTACK_ARP_SPOOFING: "Critical ARP review and MAC address table investigation",
        }
        return actions.get(attack_type, "Review event manually")

    def generate_cisco_command(self, alert_like) -> str:
        attack_type = alert_like.attack_type
        source_ip = alert_like.source_ip
        if attack_type == ATTACK_SSH_BRUTE_FORCE:
            return cisco_templates.ssh_bruteforce_command(source_ip)
        if attack_type == ATTACK_PORT_SCAN:
            return cisco_templates.port_scan_command(source_ip)
        if attack_type == ATTACK_ICMP_FLOOD:
            return cisco_templates.icmp_flood_command(source_ip)
        if attack_type == ATTACK_VLAN_VIOLATION:
            return cisco_templates.vlan_violation_command()
        if attack_type == ATTACK_ARP_SPOOFING:
            return cisco_templates.arp_spoofing_command()
        return "! No automatic command template. Review manually."

    def generate_response(self, alert_like) -> dict:
        action = self.get_action_by_attack_type(alert_like.attack_type)
        command = self.generate_cisco_command(alert_like)
        return {
            "recommended_action": action,
            "cisco_command": command,
            "explanation": "This is a suggested response for review only. Haris does not execute network commands.",
        }
