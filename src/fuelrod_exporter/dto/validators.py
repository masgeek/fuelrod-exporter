import re
from datetime import datetime
from typing import Optional, List

def validate_api_account_id(value) -> int:
    """Validate and convert api_account_id to int"""
    if value is None:
        raise ValueError("Account ID is required")

    if isinstance(value, str):
        if not value.strip():
            raise ValueError("Account ID cannot be empty")
        try:
            value = int(value.strip())
        except ValueError:
            raise ValueError("Account ID must be a valid integer")

    if not isinstance(value, int):
        raise ValueError("Account ID must be an integer")

    if value <= 0:
        raise ValueError("Account ID must be a positive integer")

    return value


def validate_opt_date(value: Optional[str]) -> Optional[str]:
    """Validate optional date format (YYYY-MM-DD)"""
    if not value:
        return None

    if isinstance(value, str) and not value.strip():
        return None

    value = value.strip() if isinstance(value, str) else str(value)

    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not pattern.match(value):
        raise ValueError("Date must be in 'YYYY-MM-DD' format")

    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date provided")

    if parsed_date > datetime.now():
        raise ValueError("Date cannot be in the future")

    if parsed_date < datetime(2000, 1, 1):
        raise ValueError("Date must be after 2000-01-01")

    return value


def validate_campaign_id(value) -> Optional[List[int]]:
    """Validate and normalize campaign IDs"""
    if not value:
        return None

    if isinstance(value, int):
        if value <= 0:
            raise ValueError("Campaign IDs must be positive integers")
        return [value]

    seen = set()
    unique_ids = []
    for id_val in value:
        if id_val not in seen:
            if id_val <= 0:
                raise ValueError("Campaign IDs must be positive integers")
            seen.add(id_val)
            unique_ids.append(id_val)

    return unique_ids or None


def validate_sort_by(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    allowed = {"id", "campaign_id", "message_id", "created_at", "updated_at"}
    if value not in allowed:
        raise ValueError(f"sort_by must be one of: {', '.join(sorted(allowed))}")
    return value


def validate_sort_order(value: Optional[str]) -> str:
    if not value:
        return "asc"
    if value.lower() not in {"asc", "desc"}:
        raise ValueError("sort_order must be 'asc' or 'desc'")
    return value.lower()
