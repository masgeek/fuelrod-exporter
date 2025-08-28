import logging
import os
import threading
from datetime import datetime
from io import BytesIO
import pandas as pd
import pytz
from flask import current_app

from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.repo.report_repo import ReportRepo
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.schemas.report_resp import ReportDataRecord, Pagination, ReportResponse
from fuelrod_exporter.config import Config

SERVER_TZ = pytz.timezone(Config.SERVER_TZ)


class ReportService:
    def __init__(self):
        self.repo = ReportRepo()
        self.logger = SharedLogger(level=logging.DEBUG).get_logger()

    def _map_to_records(self, items) -> list[ReportDataRecord]:
        """
        Internal helper to turn ORM model instances into ReportDataRecord DTOs.
        Converts datetimes to ISO strings for Excel safety (no tzinfo).
        """
        records: list[ReportDataRecord] = []
        for item in items:
            records.append(
                ReportDataRecord(
                    id=item.id,
                    api_account_id=item.api_account_id,
                    message_id=item.message_id,
                    campaign_id=item.campaign_id,
                    campaign_message_id=item.campaign_message_id,
                    sender_id=item.sender_id,
                    phone_number=item.phone_number,
                    network_identity=item.network_identity,
                    message=item.message,
                    network_name=item.network_name,
                    sms_count=item.sms_count,
                    character_count=item.character_count,
                    single_sms_cost=item.single_sms_cost,
                    actual_cost=item.actual_cost,
                    delivery_status=item.delivery_status,
                    delivered_to_handset=item.delivered_to_handset,
                    sent_to_network=item.sent_to_network,
                    description=item.description,
                    message_archived=item.message_archived,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                )
            )
        return records

    def get_paginated_reports(self, filters, page, per_page):
        query = self.repo.build_filtered_query(filters)
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        records = self._map_to_records(paginated.items)

        pagination = Pagination(
            total=paginated.total,
            pages=paginated.pages,
            current_page=paginated.page,
            per_page=paginated.per_page
        )
        return ReportResponse(
            data=records,
            pagination=pagination
        )

    def get_all_reports(self, filters):
        q = self.repo.build_filtered_query(filters)
        return q.all()

    def generate_excel_task(self, filters: ReportFilter, filename: str):

        orm_items = self.get_all_reports(filters)
        dto_records = self._map_to_records(orm_items)

        server_tz = pytz.timezone(Config.SERVER_TZ)
        serialized = []
        for r in dto_records:
            rec = {}
            for k, v in r.model_dump().items():
                if hasattr(v, "tzinfo") and v.tzinfo is not None:
                    v = v.astimezone(server_tz).replace(tzinfo=None)
                    rec[k] = v.isoformat(sep=" ")
                elif isinstance(v, datetime):
                    rec[k] = v.isoformat(sep=" ")
                else:
                    rec[k] = v
            serialized.append(rec)

        df = pd.DataFrame(serialized)
        os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)
        file_path = os.path.join(Config.EXPORT_FOLDER, filename)
        df.to_excel(file_path, index=False)
