import logging
from flask import request, jsonify, send_file
from flask_openapi3 import Tag, APIBlueprint

from fuelrod_exporter.config import Config
from fuelrod_exporter.models.common import PaginationQuery
from fuelrod_exporter.schemas.report_resp import (
    ReportResponse,
    Unauthorized, ReportDataRecord,
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
        tag = Tag(name="reports", description="Campaign reports")
        self.api = APIBlueprint(
            self.__bp__, __name__, url_prefix=url_prefix, abp_tags=[tag]
        )
        # Repo & logger
        self.service = ReportService()
        self.logger = SharedLogger(level=logging.DEBUG).get_logger()
        # Register routes
        self._register_routes()

    def _register_routes(self):
        @self.api.post("/",
                       summary="List filtered reports",
                       responses={200: ReportResponse, 401: Unauthorized}
                       )
        def list_reports(body: ReportFilter, query: PaginationQuery):
            self.logger.debug(f"Request per_page: {query}")
            try:
                paginated = self.service.get_paginated_reports(filters=body, page=query.page, per_page=query.per_page)
                return jsonify(paginated.model_dump(mode="json")), 200

            except Exception as e:
                self.logger.error(f"Error retrieving report data: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.api.post(
            "/export",
            summary="Export filtered reports to Excel and return download link",
            responses={200: {"type": "object", "properties": {"download_url": {"type": "string"}}}}
        )
        def export_reports(body: ReportFilter):
            try:

                download_url = self.service.export_reports_to_excel_file(body)
                return {"download_url": download_url}
            except Exception as e:
                self.logger.exception("Error exporting reports")
                return jsonify({"detail": str(e)}), 500
