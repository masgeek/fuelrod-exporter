from calendar import monthrange
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator, model_validator, ConfigDict, conlist

from fuelrod_exporter.models.common import ReportFilterBase
from fuelrod_exporter.schemas.validators import (
    validate_api_account_id,
    validate_campaign_id,
    validate_sort_by,
)

def subtract_months(dt: date, months: int) -> date:
    """Subtract months from a date without using dateutil."""
    year = dt.year
    month = dt.month - months
    while month <= 0:
        month += 12
        year -= 1
    day = min(dt.day, monthrange(year, month)[1])
    return date(year, month, day)

today = date.today()
first_day = subtract_months(today.replace(day=1), 3)
last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

class ReportFilter(ReportFilterBase):
    campaign_id: Optional[conlist(item_type=int)] = Field(
        None, description="One or more campaign IDs", min_length=1, max_length=50
    )

    model_config = ConfigDict(
        use_enum_values=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow",
        json_schema_extra={
            "example": {
                "api_account_id": 6,
                "campaign_id": [20200811071956, 20200811071955],
                "date_range": {"start": first_day.isoformat(), "end": last_day.isoformat()},
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        },
    )

    _validate_api_account_id = field_validator("api_account_id", mode="before")(validate_api_account_id)
    _validate_campaign_id = field_validator("campaign_id", mode="before")(validate_campaign_id)
    _validate_sort_by = field_validator("sort_by", mode="before")(validate_sort_by)

    @model_validator(mode="after")
    def cross_field_validation(self):
        if self.campaign_id and len(self.campaign_id) > 50:
            raise ValueError("Maximum 50 campaign IDs allowed per request")
        return self
