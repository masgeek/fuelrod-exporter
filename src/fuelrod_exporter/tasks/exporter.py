# fuelrod_exporter/tasks/export_tasks.py
import dramatiq
from fuelrod_exporter.worker_app import get_app
from fuelrod_exporter.schemas.report_filter import ReportFilter
from fuelrod_exporter.services.report_service import ReportService

app = get_app()
@dramatiq.actor(store_results=True)
def generate_excel_task(payload: dict, filename: str):
    with app.app_context():
        print("Starting Excel generation...")
        filters = ReportFilter(**payload)
        service = ReportService()
        service.generate_excel_task(filters, filename)
        print("Finished Excel generation")
