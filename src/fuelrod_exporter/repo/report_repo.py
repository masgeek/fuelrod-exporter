import logging
from datetime import datetime, time

from flask_sqlalchemy.pagination import QueryPagination
from sqlalchemy import desc, asc
from sqlalchemy.orm import Query

from fuelrod_exporter.models.common import SortOrder
from fuelrod_exporter.core.database import MyDb
from fuelrod_exporter.models.fuelrod_views import SmsReport
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.core.logging import SharedLogger

shared_logger = SharedLogger(level=logging.DEBUG)


class ReportRepo:
    def __init__(self):
        self.logger = shared_logger.get_logger()

    def _get_session(self):
        # Ensure that `MyDb` has been initialized with a Flask app
        self.db = MyDb.get_db()
        return self.db.session

    def build_filtered_query(self, filters: ReportFilter) -> Query:
        session = self._get_session()
        query = session.query(SmsReport)
        conditions = [
            SmsReport.api_account_id == filters.api_account_id
        ]

        if filters.campaign_id:
            conditions.append(SmsReport.campaign_id.in_(filters.campaign_id))

        if filters.date_range:
            start_dt = datetime.combine(filters.date_range.start, time.min)
            end_dt = datetime.combine(filters.date_range.end, time.max)
            conditions.extend([
                SmsReport.created_at >= start_dt,
                SmsReport.created_at <= end_dt
            ])

        query = query.filter(*conditions)
        if filters.sort_by:
            column = getattr(SmsReport, filters.sort_by)
            order_fn = desc if filters.sort_order == SortOrder.desc else asc
            query = query.order_by(order_fn(column))

        return query
