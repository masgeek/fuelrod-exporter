# fuelrod_exporter/tasks/export_tasks.py
import logging
import dramatiq
from fuelrod_exporter.worker_app import get_app
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.services.report_service import ReportService
from fuelrod_exporter.core.logging import SharedLogger

logger = SharedLogger().get_logger()
app = get_app()


@dramatiq.actor(store_results=True)
def generate_excel_task(payload: dict, filename: str):
    with app.app_context():
        try:
            logger.info("Starting Excel generation: %s", filename)
            filters = ReportFilter(**payload)
            service = ReportService()
            service.generate_excel_task(filters, filename)
            logger.info(f"Finished Excel generation:  {filename}")
        except Exception as e:
            logger.exception("Error during Excel generation: %s", filename)
            raise
