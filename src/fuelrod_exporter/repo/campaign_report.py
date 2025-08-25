import logging
from typing import Optional, List, Type

from flask_sqlalchemy.pagination import QueryPagination
from geoalchemy2 import WKTElement
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query

from fuelrod_exporter.dto.crop_data_resp import CropDataRecord
from fuelrod_exporter.dto.data_filters import CampaignReportFilter
from fuelrod_exporter.models.database_conn import MyDb
from fuelrod_exporter.models.fuelrod import t_vw_sms_reports as sms_reports
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

        query = session.query(sms_reports)

        if filters.api_account_id:
            query = query.filter(sms_reports.country == filters.country)
        if filters.province:
            # Perform partial search for province
            query = query.filter(sms_reports.province.ilike(f"%{filters.province}%"))
        if filters.variety:
            query = query.filter(sms_reports.variety == filters.variety)
        if filters.season_type:
            query = query.filter(sms_reports.season_type == filters.season_type)
        if filters.opt_date:
            query = query.filter(sms_reports.opt_date == filters.opt_date)
        if filters.planting_option is not None:
            query = query.filter(sms_reports.planting_option == filters.planting_option)

        query = query.order_by(sms_reports.id)
        return query

    def get_paginated_data(self, filters: PlantingDataFilter, page: int, per_page: int) -> QueryPagination:
        query = self.get_filtered_data(filters)

        return query.paginate(page=page, per_page=per_page, error_out=False)

    def update(self, crop_data: sms_reports) -> sms_reports:
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

    def delete(self, crop_data: sms_reports) -> None:
        session = self._get_session()
        try:
            session.delete(crop_data)
            session.commit()
            self.logger.info(f"Deleted PlantingData with ID: {crop_data.id}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to delete PlantingData with ID {crop_data.id}: {e}")
            raise

    def find_by_checksum(self, check_sum: str) -> Optional[sms_reports]:
        session = self._get_session()
        try:
            crop_data = (session.query(sms_reports)
                         .filter_by(check_sum=check_sum).first())
            self.logger.info(f"Retrieved PlantingData with checksum: {check_sum}")
            return crop_data
        except Exception as e:
            self.logger.error(f"Failed to find PlantingData with checksum {check_sum}: {e}")
            raise

    def batch_insert(self, crop_data: List[CropDataRecord]) -> None:
        if not crop_data:
            self.logger.warning("No records to insert.")
            return

        session = self._get_session()
        try:
            # Prepare the data for insertion
            mappings = [
                {
                    **record.__dict__,
                    'coordinates': WKTElement(f"POINT({record.lon} {record.lat})", srid=4326)
                    if record.lat and record.lon
                    else None
                }
                for record in crop_data
            ]

            # Perform the bulk insert
            session.bulk_insert_mappings(sms_reports, mappings)
            session.commit()
            self.logger.info(f"Batch inserted {len(crop_data)} CropData records")
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Failed to batch insert CropData records: {e}")
            raise
        except Exception as e:
            session.rollback()
            self.logger.error(f"An unexpected error occurred: {e}")
            raise
