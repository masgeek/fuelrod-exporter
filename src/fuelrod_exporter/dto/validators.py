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