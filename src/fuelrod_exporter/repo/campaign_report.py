import logging
from typing import Optional, List, Type

from flask_sqlalchemy.pagination import QueryPagination
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query

from fuelrod_exporter.dto.data_filters import CampaignReportFilter
from fuelrod_exporter.models.database_conn import MyDb
from fuelrod_exporter.models.fuelrod_views import SmsReport
from fuelrod_exporter.utils.logging import SharedLogger

shared_logger = SharedLogger(level=logging.DEBUG)


class CropDataRepo:
    def __init__(self):
        self.logger = shared_logger.get_logger()

    def _get_session(self):
        # Ensure that `MyDb` has been initialized with a Flask app
        self.db = MyDb.get_db()
        return self.db.session

    def get_filtered_data(self, filters: CampaignReportFilter) -> Query:

        session = self._get_session()

        query = session.query(SmsReport)

        if filters.api_account_id:
            query = query.filter(SmsReport.api_account_id == filters.api_account_id)
        if filters.campaign_id:
            # Perform a partial search for a province
            query = query.filter(SmsReport.campaign_id.ilike(f"%{filters.campaign_id}%"))

        query = query.order_by(SmsReport.id)
        return query

    def get_paginated_data(self, filters: CampaignReportFilter, page: int, per_page: int) -> QueryPagination:
        query = self.get_filtered_data(filters)

        return query.paginate(page=page, per_page=per_page, error_out=False)

    def update(self, crop_data: SmsReport) -> SmsReport:
        session = self._get_session()
        try:
            session.commit()
            session.refresh(crop_data)
            self.logger.info(f"Updated PlantingData with ID: {crop_data.id}")
            return crop_data
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to update PlantingData with ID {crop_data.id}: {e}")
            raise
