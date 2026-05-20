from ipaddress import ip_address


def normalize_ip(value: str | None) -> str | None:
    if not value:
        return None
    return str(ip_address(value.strip()))
