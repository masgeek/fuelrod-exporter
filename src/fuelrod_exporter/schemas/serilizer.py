from datetime import date, datetime


def serialize_dates(data: dict) -> dict:
    """Recursively convert date/datetime to ISO strings in a dict."""
    for k, v in data.items():
        if isinstance(v, (datetime, date)):
            data[k] = v.isoformat()
        elif isinstance(v, dict):
            data[k] = serialize_dates(v)
        elif isinstance(v, list):
            data[k] = [serialize_dates(i) if isinstance(i, dict) else i for i in v]
    return data
