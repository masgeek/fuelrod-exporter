# celery_worker.py
from fuelrod_exporter import create_app

app = create_app()
app.app_context().push()
