import logging

from flask import request, jsonify
from flask_openapi3 import Tag, APIBlueprint

from fuelrod_exporter.config import API_PREFIX
from fuelrod_exporter.schemas.report_resp import ReportResponse, ReportDataRecord, Unauthorized, Pagination
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.repo.reports_repo import ReportRepo
from fuelrod_exporter.core.logging import SharedLogger

__bp__ = "/reports/campaign"
__version__ = "/v1"

url_prefix = API_PREFIX + __version__ + __bp__

# Define any security requirements or tags if needed
tag = Tag(name="fuelrod", description="Campaign reports")

api = APIBlueprint(__bp__, __name__, url_prefix=url_prefix, abp_tags=[tag])

shared_logger = SharedLogger(level=logging.DEBUG)
logger = shared_logger.get_logger()

planting_data_repo = ReportRepo()


@api.post(
    '/',
    responses={200: ReportResponse, 401: Unauthorized}
)
def get_data(body: ReportFilter):
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=50, type=int)

    try:
        paginated = planting_data_repo.get_paginated_data(filters=body, page=page, per_page=per_page)

        # Build a list of Pydantic DTOs
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
        response_dto = ReportResponse(
            data=records,
            pagination=pagination
        )

        # Serialize to plain dict for Flask’s jsonify
        return jsonify(response_dto.model_dump(mode='json')), 200

    except Exception as e:
        logger.error(f"Error retrieving report data: {e}")
        return jsonify({'error': str(e)}), 500
