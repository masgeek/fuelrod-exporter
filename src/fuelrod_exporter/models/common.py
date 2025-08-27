from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# noinspection PyNestedDecorators
class DateRange(BaseModel):
    start: date = Field(..., description="Inclusive start date (YYYY-MM-DD)")
    end: date = Field(..., description="Inclusive end date (YYYY-MM-DD)")

    model_config = ConfigDict(extra="forbid")

    @field_validator("end")
    @classmethod
    def check_end_on_or_after_start(cls, end_value, info):
        start_value = info.data.get("start")
        if start_value and end_value < start_value:
            raise ValueError("end must be on or after start")
        return end_value


class ReportFilterBase(BaseModel):
    api_account_id: int = Field(..., description="Account id")
    date_range: Optional[DateRange] = Field(
        None, description="Object with `start` and `end` dates"
    )
    sort_by: Optional[str] = Field(None, description="Column to sort by")
    sort_order: Optional[SortOrder] = Field(SortOrder.asc, description="Sort order: 'asc' or 'desc'")
