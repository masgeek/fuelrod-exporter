import re


def format_size(bytes_size: int) -> str:
    """Format byte size into human-readable units, defaulting to KB."""
    if bytes_size <= 0:
        return "0.0 KB"

    units = ["KB", "MB", "GB", "TB", "PB"]
    size = bytes_size / 1024  # Start from KB

    for unit in units:
        if size < 1024:
            precision = 1 if unit in ["KB", "MB"] else 2
            return f"{size:.{precision}f} {unit}"
        size /= 1024

    # Fallback in case size exceeds all units
    return f"{size:.2f} PB"


def format_age(seconds: int) -> str:
    """Format duration in human-readable form, starting from seconds."""
    if seconds <= 0:
        return "0 sec"

    units = [
        ("sec", 60),
        ("min", 60),
        ("h", 24),
        ("d", 30),
        ("mo", 12),
        ("y", float("inf")),
    ]

    value = seconds
    for unit, threshold in units:
        if value < threshold:
            return f"{int(value)} {unit}"
        value /= threshold

    # Fallback (should never hit this)
    return f"{int(value)} y"


def parse_interval_to_seconds(interval_str: str) -> int:
    """
    Converts interval strings like '30s', '15m', '2h', '1d', '1y' into seconds.
    """
    match = re.match(r"^(\d+)([smhdy])$", interval_str.strip().lower())
    if not match:
        raise ValueError(f"Invalid SCHEDULER_INTERVAL format: '{interval_str}'")

    value, unit = match.groups()
    value = int(value)

    unit_multipliers = {
        "s": 1,            # seconds
        "m": 60,           # minutes
        "h": 3600,         # hours
        "d": 86400,        # days
        "y": 31536000      # years (365 days)
    }


    return value * unit_multipliers[unit]


import re

def parse_env_list(raw_list: str) -> set[str]:
    """
    Parses an environment variable string into a set of lowercase items,
    splitting by comma, space, semicolon, or colon.
    """
    if not raw_list:
        return set()

    # Split by any of: comma, space, semicolon, colon
    items = re.split(r"[,\s;:]+", raw_list.strip())
    return {item.lower() for item in items if item}