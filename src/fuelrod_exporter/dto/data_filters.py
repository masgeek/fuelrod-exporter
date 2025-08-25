import re
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class CampaignReportFilter:
    api_account_id: int = Field(None, description='Account id')
    campaign_id: Optional[int] = Field(None, description='Campaign id')


# noinspection PyNestedDecorators
class ReportFilter(BaseModel, CampaignReportFilter):
    model_config = ConfigDict(
        use_enum_values=True,
        str_strip_whitespace=True
    )

    @field_validator('opt_date', mode='before')
    @classmethod
    def validate_opt_date(cls, value):
        """
        Validate that the date is in 'YYYY-MM-DD' format.
        """
        if value:
            pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            if not pattern.match(value):
                raise ValueError("Date must be in 'YYYY-MM-DD' format.")
        return value
