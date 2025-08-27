from typing import List, Optional

from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


class Unauthorized(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Unauthorized!", description="Exception Information")


class ReportDataRecord(BaseModel):
    id: int
    api_account_id: int
    message_id: Optional[str]
    campaign_id: Optional[int]
    campaign_message_id: Optional[int]
    sender_id: str
    phone_number: str
    network_identity: str
    message: str
    network_name: str
    sms_count: int
    character_count: int
    single_sms_cost: Decimal
    actual_cost: Decimal
    delivery_status: str
    delivered_to_handset: bool
    sent_to_network: bool
    description: Optional[str]
    message_archived: bool
    created_at: datetime
    updated_at: datetime


class Pagination(BaseModel):
    total: int
    pages: int
    current_page: int
    per_page: int


class ReportResponse(BaseModel):
    data: List[ReportDataRecord]
    pagination: Pagination
