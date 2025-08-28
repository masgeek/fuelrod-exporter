# fuelrod_exporter/tasks/system_tasks.py

from fuelrod_exporter.core.celery import my_celery as celery
import datetime
import time


@celery.task(bind=True, name="system.health_check")
def health_check_task(self):
    """
    Lightweight end-to-end healthcheck.
    Ensures worker, broker, and result backend are functional.
    """
    return {
        "status": "ok",
        "worker_id": self.request.id,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "response_time": time.time(),
    }


@celery.task(bind=True, name="system.test_database")
def test_database_task(self):
    """
    Test database connectivity from within a Celery task.
    Validates that workers can reach the database.
    """
    try:
        from fuelrod_exporter.core.database import MyDb

        result = MyDb.get_db().session.execute("SELECT 1").fetchone()
        return {
            "status": "success",
            "message": "Database connection successful from worker",
            "result": result[0] if result else None,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed from worker: {str(e)}",
        }
