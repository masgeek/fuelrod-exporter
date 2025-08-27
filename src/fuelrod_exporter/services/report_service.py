from flask import current_app
from fuelrod_exporter.repo.report_repo import ReportRepo


class ReportService:
    def get_paginated_reports(session, filters, page, per_page):
        base_q = build_filtered_query(session, filters)
        return base_q.paginate(page=page, per_page=per_page)


    def export_reports_to_excel(records):
        # your Excel‐builder logic here
        ...
