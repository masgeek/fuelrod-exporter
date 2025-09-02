import os
from datetime import datetime

import xlsxwriter
from dateutil import tz
from fuelrod_exporter.config import Config
from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.repo.report_repo import ReportRepo
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.schemas.report_resp import ReportDataRecord, Pagination, ReportResponse
from fuelrod_exporter.services.minio_service import MinioService
import inflect

SERVER_TZ = tz.gettz(Config.SERVER_TZ)  # e.g., "Africa/Nairobi"
p = inflect.engine()

ACRONYM_OVERRIDES = {
    "id": "ID",
    "api": "API",
    "sms": "SMS",
    "url": "URL",
}

HEADER_OVERRIDES = {
    "api_account_id": "Account",
    # "single_sms_cost": "Single Message Cost",
    "network_identity": "Network name"
}


class ReportService:

    def __init__(
            self,
            header_overrides: dict[str, str] | None = None,
            acronym_overrides: dict[str, str] | None = None,
    ):
        self.repo = ReportRepo()
        self.logger = SharedLogger().get_logger()
        self.minio = MinioService()

        # ✅ merge global + instance config
        self.header_overrides = {**HEADER_OVERRIDES, **(header_overrides or {})}
        self.acronym_overrides = {**ACRONYM_OVERRIDES, **(acronym_overrides or {})}

    # noinspection PyMethodMayBeStatic
    def _map_to_record(self, item) -> ReportDataRecord:
        """Convert a single ORM model instance into a ReportDataRecord DTO."""
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
            updated_at=item.updated_at,
        )

    def _map_to_records(self, items) -> list[ReportDataRecord]:
        """Convert ORM model instances into ReportDataRecord DTOs."""
        return [self._map_to_record(item) for item in items]

    # noinspection PyTypeChecker
    def _humanize_header(self, header: str) -> str:
        """
        Convert snake_case header names into human-friendly labels,
        respecting overrides, acronyms.
        """
        # Check manual override first
        if header in self.header_overrides:
            return self.header_overrides[header]

        parts = header.split("_")
        human_parts = []
        for part in parts:
            # ✅ check acronyms first
            if part.lower() in self.acronym_overrides:
                word = self.acronym_overrides[part.lower()]
            else:
                # ✅ keep inflect only for real plurals (like "users" → "User")
                word = p.singular_noun(part) or part
                word = word.capitalize()

            human_parts.append(word)
        return " ".join(human_parts)

    # noinspection PyUnresolvedReferences
    def get_paginated_reports(self, filters, page, per_page):
        query = self.repo.build_filtered_query(filters)
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        records = self._map_to_records(paginated.items)
        pagination = Pagination(
            total=paginated.total,
            pages=paginated.pages,
            current_page=paginated.page,
            per_page=paginated.per_page,
        )
        return ReportResponse(data=records, pagination=pagination)

    def get_all_reports(self, filters):
        q = self.repo.build_filtered_query(filters)
        return q.all()

    def generate_excel_task(self, filters: ReportFilter, filename: str):
        """
        Generates an Excel file with one sheet per campaign.
        Fully streaming: no .count(), no big memory usage.
        """
        if not os.path.exists(Config.EXPORT_FOLDER):
            os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)
        file_path = os.path.join(Config.EXPORT_FOLDER, filename)

        self.logger.info(f"Starting Excel export: {file_path}")
        workbook = xlsxwriter.Workbook(file_path)
        bold_format = workbook.add_format({"bold": True})

        # Headers come directly from the ReportDataRecord schema
        headers = list(ReportDataRecord.model_fields.keys())

        campaign_ids = filters.campaign_id or [None]

        for cid in campaign_ids:
            query = self._build_query_for_campaign(filters, cid)
            row_count = self._stream_to_sheet(workbook, cid, headers, bold_format, query)

            if row_count == 0:
                self.logger.info(f"No records found for campaign: {cid}")
            else:
                sheet_name = f"Campaign_{cid}" if cid else "All"
                self.logger.info(f"Finished sheet '{sheet_name[:31]}' with {row_count} rows")

        workbook.close()
        self.logger.success(f"Excel export complete: {file_path}")

        object_name = self.minio.upload_file(file_path, filename)
        self.logger.debug(f"Uploaded to MinIO as {object_name}")

    def _build_query_for_campaign(self, filters, campaign_id):
        query = self.repo.build_filtered_query(filters)
        if campaign_id:
            query = query.filter_by(campaign_id=campaign_id)
        return query.yield_per(500)  # streaming, avoids loading all in memory

    def _stream_to_sheet(self, workbook, campaign_id, headers, bold_format, query):
        """
        Write streamed query results to an Excel sheet.
        Returns number of rows written.
        """
        iterator = query.__iter__()  # get iterator without materializing
        try:
            first_item = next(iterator)
        except StopIteration:
            return 0  # no rows at all

        # Create worksheet only if we have data
        sheet_name = f"Campaign_{campaign_id}" if campaign_id else "All"
        worksheet = workbook.add_worksheet(sheet_name[:31])

        # Write headers
        readable_headers = [self._humanize_header(h) for h in headers]
        for col_idx, header in enumerate(readable_headers):
            worksheet.write(0, col_idx, header, bold_format)

        col_widths = [len(str(h)) for h in headers]
        row_idx = 1
        row_count = 0

        # Write the first row
        row_idx, row_count = self._write_row(worksheet, row_idx, first_item, col_widths, row_count)

        # Stream the rest
        for item in iterator:
            row_idx, row_count = self._write_row(worksheet, row_idx, item, col_widths, row_count)

        # Adjust column widths
        for col_idx, width in enumerate(col_widths):
            worksheet.set_column(col_idx, col_idx, min(width + 2, 50))

        return row_count

    def _write_row(self, worksheet, row_idx, item, col_widths, row_count):
        record = self._map_to_record(item)
        for col_idx, (k, v) in enumerate(record.model_dump().items()):
            value = self._format_value(v)
            worksheet.write(row_idx, col_idx, value)
            col_widths[col_idx] = max(col_widths[col_idx], len(str(value)))
        return row_idx + 1, row_count + 1

    @staticmethod
    def _format_value(v):
        """Convert datetime to ISO string or return value as-is."""
        if isinstance(v, datetime) and v.tzinfo is not None:
            v = v.astimezone(SERVER_TZ).replace(tzinfo=None)
            return v.isoformat(sep=" ")
        elif isinstance(v, datetime):
            return v.isoformat(sep=" ")
        return v
