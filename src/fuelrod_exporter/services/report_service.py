import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import xlsxwriter
from dateutil import tz
from fuelrod_exporter.config import Config
from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.repo.report_repo import ReportRepo
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.schemas.report_resp import ReportDataRecord, Pagination, ReportResponse

SERVER_TZ = tz.gettz(Config.SERVER_TZ)  # e.g., "Africa/Nairobi"


class ReportService:
    def __init__(self):
        self.repo = ReportRepo()
        self.logger = SharedLogger().get_logger()

    def _map_to_record(self, item) -> ReportDataRecord:
        """
        Convert a single ORM model instance into a ReportDataRecord DTO.
        """
        return ReportDataRecord(
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

    def _map_to_records(self, items) -> list[ReportDataRecord]:
        """
        Internal helper to turn ORM model instances into ReportDataRecord DTOs.
        Converts datetimes to ISO strings for Excel safety (no tzinfo).
        """
        records: list[ReportDataRecord] = []
        for item in items:
            records.append(
                self._map_to_record(item)
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
        """
        Generates an Excel file using XlsxWriter with one sheet per campaign.
        Includes bold headers and auto-adjusted column widths.
        """
        os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)
        file_path = os.path.join(Config.EXPORT_FOLDER, filename)

        self.logger.info(f"Starting Excel export: {file_path}")
        workbook = xlsxwriter.Workbook(file_path)
        bold_format = workbook.add_format({'bold': True})

        # Determine campaign IDs
        campaign_ids = filters.campaign_id or [None]  # None = "All"

        for cid in campaign_ids:
            # Build filtered query per campaign
            query = self.repo.build_filtered_query(filters)
            if cid:
                query = query.filter_by(campaign_id=cid)

            query = query.yield_per(500)

            first_item = query.first()
            if not first_item:
                self.logger.info(f"No records found for campaign: {cid}")
                continue

            headers = list(self._map_to_record(first_item).model_dump().keys())
            sheet_name = f"Campaign_{cid}" if cid else "All"
            sheet_name = sheet_name[:31]
            worksheet = workbook.add_worksheet(sheet_name)

            # Write headers with bold format
            for col_idx, header in enumerate(headers):
                worksheet.write(0, col_idx, header, bold_format)

            # Track column widths
            col_widths = [len(str(h)) for h in headers]

            # Write first row
            record = self._map_to_record(first_item)
            for col_idx, (k, v) in enumerate(record.model_dump().items()):
                value = self._format_value(v)
                worksheet.write(1, col_idx, value)
                col_widths[col_idx] = max(col_widths[col_idx], len(str(value)))

            # Write remaining rows
            row_idx = 2
            for item in query:
                record = self._map_to_record(item)
                for col_idx, (k, v) in enumerate(record.model_dump().items()):
                    value = self._format_value(v)
                    worksheet.write(row_idx, col_idx, value)
                    col_widths[col_idx] = max(col_widths[col_idx], len(str(value)))
                row_idx += 1

            # Adjust column widths
            for col_idx, width in enumerate(col_widths):
                worksheet.set_column(col_idx, col_idx, min(width + 2, 50))  # max width 50

            self.logger.info(f"Finished sheet '{sheet_name}' with {row_idx - 1} rows")

        workbook.close()
        self.logger.success(f"Excel export complete: {file_path}")

    @staticmethod
    def _format_value(v):
        """Convert datetime to ISO string or return value as-is"""
        if isinstance(v, datetime) and v.tzinfo is not None:
            v = v.astimezone(SERVER_TZ).replace(tzinfo=None)
            return v.isoformat(sep=" ")
        elif isinstance(v, datetime):
            return v.isoformat(sep=" ")
        return v
