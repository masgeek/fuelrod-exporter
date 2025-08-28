import datetime
import time
# import dramatiq
from fuelrod_exporter.core.broker import redis_broker as dramatiq
from fuelrod_exporter.core.database import MyDb


@dramatiq.actor(store_results=True)
def health_check_task():
    """
    Lightweight end-to-end healthcheck.
    Ensures worker and broker are functional.
    """
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "response_time": time.time(),
    }


@dramatiq.actor(store_results=True)
def test_database_task():
    """
    Test database connectivity from within a Dramatiq task.
    Validates that workers can reach the database.
    """
    try:

        result = MyDb.check_db_execution()
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
