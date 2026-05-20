from __future__ import annotations

from dataclasses import dataclass

from apps.incidents.models import Alert

from ..models import ResponseAction


@dataclass
class ResponsePreview:
    action_type: str
    title: str
    description: str
    recommended_action: str
    cisco_ios_commands: list[str]
    risk_level: str
    requires_approval: bool = True

    @property
    def command_text(self):
        return "\n".join(self.cisco_ios_commands)

    def as_dict(self):
        return {
            "action_type": self.action_type,
            "title": self.title,
            "description": self.description,
            "recommended_action": self.recommended_action,
            "cisco_ios_commands": self.cisco_ios_commands,
            "command_text": self.command_text,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
        }


class ResponseGenerator:
    def generate_for_alert(self, alert: Alert) -> ResponseAction:
        if hasattr(alert, "response_action"):
            return alert.response_action
        preview = self.preview(alert.attack_type, alert.source_ip, alert.destination_ip, alert.evidence)
        approval_status = ResponseAction.ApprovalStatuses.PENDING if preview.requires_approval else ResponseAction.ApprovalStatuses.NOT_REQUIRED
        return ResponseAction.objects.create(
            alert=alert,
            action_type=preview.action_type,
            title=preview.title,
            description=preview.description,
            recommended_action=preview.recommended_action,
            cisco_ios_commands=preview.cisco_ios_commands,
            command_text=preview.command_text,
            risk_level=preview.risk_level,
            requires_approval=preview.requires_approval,
            approval_status=approval_status,
        )

    def preview(self, attack_type, source_ip, destination_ip=None, evidence=None) -> ResponsePreview:
        alert = _PreviewAlert(attack_type=attack_type, source_ip=source_ip, destination_ip=destination_ip, evidence=evidence or {})
        method = getattr(self, f"generate_{attack_type}_response", self.generate_default_response)
        return method(alert)

    def generate_ssh_bruteforce_response(self, alert) -> ResponsePreview:
        commands = [
            "conf t",
            "ip access-list extended HARIS_BLOCK_LIST",
            f"deny ip host {alert.source_ip} any",
            "permit ip any any",
            "interface <interface_name_or_placeholder>",
            "ip access-group HARIS_BLOCK_LIST in",
            "end",
            "write memory",
        ]
        return ResponsePreview("block_ip", "Block SSH brute force source", "Blocks repeated failed SSH source traffic with an IOS ACL.", "Review and apply an ingress ACL blocking the attacking source IP.", commands, "medium")

    def generate_port_scan_response(self, alert) -> ResponsePreview:
        destination = alert.destination_ip or "any"
        host_target = f"host {destination}" if destination != "any" else "any"
        commands = [
            "conf t",
            "ip access-list extended HARIS_PORT_SCAN_BLOCK",
            f"deny ip host {alert.source_ip} {host_target}",
            "permit ip any any",
            "end",
            "write memory",
        ]
        return ResponsePreview("block_ip", "Block or monitor port scanner", "Suggests blocking scanner traffic to the scanned destination.", "Block the scanner if confirmed malicious, or monitor if this is a training lab.", commands, "medium")

    def generate_icmp_flood_response(self, alert) -> ResponsePreview:
        commands = [
            "conf t",
            "ip access-list extended HARIS_ICMP_CONTROL",
            f"deny icmp host {alert.source_ip} any echo",
            "permit ip any any",
            "end",
            "write memory",
        ]
        return ResponsePreview("rate_limit", "Control ICMP flood source", "Suggests restricting ICMP echo from the source.", "Apply ICMP controls or rate limits after confirming the traffic is abusive.", commands, "high")

    def generate_vlan_violation_response(self, alert) -> ResponsePreview:
        commands = [
            "conf t",
            "ip access-list extended HARIS_VLAN_RESTRICT",
            "deny ip <source_vlan_network_placeholder> <wildcard_mask_placeholder> <destination_vlan_network_placeholder> <wildcard_mask_placeholder>",
            "permit ip any any",
            "end",
            "write memory",
        ]
        return ResponsePreview("enhance_acl", "Enhance VLAN boundary ACL", "Suggests adding ACL controls between restricted VLANs.", "Review allowed inter-VLAN paths and enforce the intended segmentation policy.", commands, "medium")

    def generate_arp_spoofing_response(self, alert) -> ResponsePreview:
        ip_address = alert.evidence.get("ip_address") or alert.source_ip
        macs = alert.evidence.get("mac_addresses") or [alert.evidence.get("mac_address") or "<mac_address_placeholder>"]
        commands = [
            "conf t",
            f"arp {ip_address} {macs[0]} arpa",
            "end",
            "write memory",
        ]
        return ResponsePreview("bind_ip_mac", "Investigate ARP spoofing indicator", "Suggests validating and binding the expected IP/MAC mapping.", "Investigate switch CAM/ARP tables and apply binding only after validating the legitimate MAC.", commands, "high")

    def generate_default_response(self, alert) -> ResponsePreview:
        commands = ["conf t", "! Review alert evidence before applying changes", "end"]
        return ResponsePreview("investigate", "Investigate alert", "No specific playbook matched this alert type.", "Review the evidence and select a manual response.", commands, "low", requires_approval=False)


class _PreviewAlert:
    def __init__(self, attack_type, source_ip, destination_ip=None, evidence=None):
        self.attack_type = attack_type
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.evidence = evidence or {}
