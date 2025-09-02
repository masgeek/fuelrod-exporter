import re


def format_size(bytes_size: int) -> str:
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 ** 2:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 ** 3:
        return f"{bytes_size / (1024 ** 2):.1f} MB"
    else:
        return f"{bytes_size / (1024 ** 3):.2f} GB"

def format_age(seconds: int) -> str:
    """Format age in human-readable form."""
    if seconds < 60:
        return f"{seconds} sec"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} h"
    days = hours // 24
    if days < 30:
        return f"{days} d"
    months = days // 30
    if months < 12:
        return f"{months} mo"
    years = months // 12
    return f"{years} y"

def parse_interval_to_seconds(interval_str: str) -> int:
    """
    Converts interval strings like '30s', '15m', '2h', '1d' into seconds.
    """
    match = re.match(r"^(\d+)([smhd])$", interval_str.strip().lower())
    if not match:
        raise ValueError(f"Invalid SCHEDULER_INTERVAL format: '{interval_str}'")

    value, unit = match.groups()
    value = int(value)

    unit_multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400
    }

    return value * unit_multipliers[unit]
