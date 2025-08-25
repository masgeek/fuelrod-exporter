from typing import List, Optional

from pydantic import Field, BaseModel


class Unauthorized(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Unauthorized!", description="Exception Information")

class ReportDataRecord(BaseModel):
    file_name: Optional[str]
    check_sum: Optional[str]


class Pagination(BaseModel):
    total: int
    pages: int
    current_page: int
    per_page: int


class CampaignReportResponse(BaseModel):
    data: List[ReportDataRecord]
    pagination: Pagination
