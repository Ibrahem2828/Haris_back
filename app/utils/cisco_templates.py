def ssh_bruteforce_command(source_ip: str) -> str:
    return "\n".join(
        [
            f"access-list 100 deny ip host {source_ip} any",
            "access-list 100 permit ip any any",
            "interface g0/0",
            "ip access-group 100 in",
        ]
    )


def port_scan_command(source_ip: str) -> str:
    return "\n".join(
        [
            f"access-list 101 deny ip host {source_ip} any",
            "access-list 101 permit ip any any",
        ]
    )


def icmp_flood_command(source_ip: str) -> str:
    return "\n".join(
        [
            f"access-list 102 deny icmp host {source_ip} any",
            "access-list 102 permit ip any any",
        ]
    )


def vlan_violation_command(source_network: str = "<source_network>", destination_network: str = "<destination_network>", wildcard_mask: str = "<wildcard_mask>") -> str:
    return "\n".join(
        [
            f"access-list 120 deny ip {source_network} {wildcard_mask} {destination_network} {wildcard_mask}",
            "access-list 120 permit ip any any",
        ]
    )


def arp_spoofing_command() -> str:
    return "\n".join(
        [
            "show ip arp",
            "show mac address-table",
            "clear arp-cache",
        ]
    )
