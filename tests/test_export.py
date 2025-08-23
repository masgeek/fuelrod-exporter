import json
from fuelrod_exporter import create_app

def test_export_json():
    app = create_app()
    client = app.test_client()

    response = client.post("/export/outbox", json={
        "filters": {"message_status": "DELIVERED"},
        "columns": ["message_id", "phone_number"],
        "export": "json"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
