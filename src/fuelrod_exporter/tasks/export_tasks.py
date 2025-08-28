# fuelrod_exporter/tasks/export_tasks.py
import os
import pandas as pd
from datetime import datetime
from io import BytesIO
import pytz

from fuelrod_exporter.core.celery import my_celery as celery
from fuelrod_exporter.config import Config
from fuelrod_exporter.services.report_service import ReportService
from fuelrod_exporter.schemas.report_filter import ReportFilter


@celery.task(name="tasks.generate_excel")
def generate_excel_task(payload: dict, filename: str):
    filters = ReportFilter(**payload)
    service = ReportService()

    orm_items = service.get_all_reports(filters)
    dto_records = service._map_to_records(orm_items)

    SERVER_TZ = pytz.timezone(Config.SERVER_TZ)
    serialized = []
    for r in dto_records:
        rec = {}
        for k, v in r.model_dump().items():
            if hasattr(v, "tzinfo") and v.tzinfo is not None:
                v = v.astimezone(SERVER_TZ).replace(tzinfo=None)
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
