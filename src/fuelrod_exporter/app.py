from flask import request, jsonify, Response
from io import BytesIO
import openpyxl
from collections import defaultdict

from . import models
from .services.export_service import query_model


def safe_sheet_name(name: str, prefix: str = "", fallback: str = "Sheet") -> str:
    """
    Ensure Excel sheet names are valid:
    - Max length 31 chars
    - No special chars: : \ / ? * [ ]
    """
    invalid_chars = set(r'\/:*?[]')
    clean_name = "".join(c for c in name if c not in invalid_chars).strip()
    if not clean_name:
        clean_name = fallback
    full_name = f"{prefix}{clean_name}"
    return full_name[:31]


def register_routes(app):
    @app.route("/export/outbox", methods=["POST"])
    def export_outbox():
        """
        Export SmsOutbox records.

        Payload example:
        {
            "filters": {"message_status": "DELIVERED"},
            "columns": ["message_id", "phone_number", "message_status"],
            "export": "excel",
            "group_by": "message_status",
            "sheet_prefix": "Outbox_"
        }
        """
        payload = request.get_json(force=True)
        filters = payload.get("filters", {})
        columns = payload.get("columns")
        export_format = payload.get("export", "json").lower()
        group_by = payload.get("group_by")  # column to split sheets
        sheet_prefix = payload.get("sheet_prefix", "")

        data = query_model(models.SmsOutbox, filters, columns)

        if export_format == "json":
            return jsonify(data)

        elif export_format == "excel":
            wb = openpyxl.Workbook()

            if group_by and data:
                grouped = defaultdict(list)
                for row in data:
                    key = row.get(group_by, "Unknown")
                    grouped[key].append(row)

                # Remove default sheet
                wb.remove(wb.active)

                for key, rows in grouped.items():
                    sheet_name = safe_sheet_name(str(key), prefix=sheet_prefix)
                    ws = wb.create_sheet(title=sheet_name)
                    ws.append(list(rows[0].keys()))
                    for r in rows:
                        ws.append(list(r.values()))
            else:
                ws = wb.active
                ws.title = safe_sheet_name("SmsOutbox", prefix=sheet_prefix)
                if data:
                    ws.append(list(data[0].keys()))
                    for row in data:
                        ws.append(list(row.values()))

            output = BytesIO()
            wb.save(output)
            output.seek(0)

            return Response(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=export.xlsx"},
            )

        else:
            return jsonify({"error": "Unsupported export format"}), 400
