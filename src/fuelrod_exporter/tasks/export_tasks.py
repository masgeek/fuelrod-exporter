# fuelrod_exporter/tasks/export_tasks.py
import os
from datetime import datetime

import pandas as pd
import pytz

import dramatiq
from fuelrod_exporter.config import Config
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.services.report_service import ReportService


@dramatiq.actor
def generate_excel_task(payload: dict, filename: str):
    filters = ReportFilter(**payload)
    service = ReportService()

    orm_items = service.get_all_reports(filters)
    dto_records = service._map_to_records(orm_items)

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
