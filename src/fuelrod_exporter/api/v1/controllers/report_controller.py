import logging
from flask import request, jsonify
from flask_openapi3 import Tag, APIBlueprint

from fuelrod_exporter.config import Config
from fuelrod_exporter.schemas.report_resp import (
    ReportResponse,
    Unauthorized,
)
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.services.report_service import ReportService


class ReportsController:
    __bp__ = "/reports/campaign"
    __version__ = "/v1"

    def __init__(self):
        # Setup URL prefix
        url_prefix = Config.API_PREFIX + self.__version__ + self.__bp__

        # Setup tags & blueprint
        tag = Tag(name="fuelrod", description="Campaign reports")
        self.api = APIBlueprint(
            self.__bp__, __name__, url_prefix=url_prefix, abp_tags=[tag]
        )
        # Repo & logger
        self.service = ReportService()
        self.logger = SharedLogger(level=logging.DEBUG).get_logger()
        # Register routes
        self._register_routes()

    def _register_routes(self):
        @self.api.post("/", responses={200: ReportResponse, 401: Unauthorized})
        def list_reports(body: ReportFilter):
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=50, type=int)

            try:
                paginated = self.service.get_paginated_reports(filters=body, page=page, per_page=per_page)
                return jsonify(paginated.model_dump(mode="json")), 200

            except Exception as e:
                self.logger.error(f"Error retrieving report data: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500
