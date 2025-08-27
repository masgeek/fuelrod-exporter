from flask import current_app
from fuelrod_exporter.repo.report_repo import ReportRepo
from fuelrod_exporter.schemas.report_resp import ReportDataRecord, Pagination, ReportResponse


class ReportService:
    def __init__(self):
        self.repo = ReportRepo()

    def get_paginated_reports(self, filters, page, per_page):
        query = self.repo.build_filtered_query(filters);
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        records = [
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
            for item in paginated.items
        ]

        # Wrap into the outer response DTO
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

    def export_reports_to_excel(self, records):
        # your Excel‐builder logic here
        ...
