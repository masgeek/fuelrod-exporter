import logging
from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

from fuelrod_exporter.config import Config
from fuelrod_exporter.core.database import MyDb
from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.core.celery import my_celery as celery
from fuelrod_exporter.tasks.system_tasks import (
    health_check_task,
    test_database_task,
)


class HealthController:
    __bp__ = "/health"
    __version__ = ""

    def __init__(self):
        # Setup URL prefix
        url_prefix = Config.API_PREFIX + self.__version__ + self.__bp__

        # Setup tags & blueprint
        tag = Tag(name="health", description="Health report")
        self.api = APIBlueprint(
            self.__bp__, __name__, url_prefix=url_prefix, abp_tags=[tag]
        )

        # Repo & logger
        self.logger = SharedLogger(level=logging.DEBUG).get_logger()

        # Register routes
        self._register_routes()

    def _register_routes(self):
        @self.api.get("/", summary="Combined health check")
        def health_check():
            status = {
                "status": "healthy",
                "components": {
                    "database": "unknown",
                    "celery": "unknown",
                },
            }

            # Check DB
            try:
                db_connected = MyDb.check_db_connection()
                status["components"]["database"] = "UP" if db_connected else "DOWN"
                if not db_connected:
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Database health check failed: {str(e)}")
                status["components"]["database"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            # Check Celery (using DB test task)
            try:
                result = test_database_task.delay()
                result_value = result.get(timeout=30)

                if result_value.get("status") == "success":
                    status["components"]["celery"] = "UP"
                else:
                    status["components"]["celery"] = "DOWN"
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Celery health check failed: {str(e)}")
                status["components"]["celery"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            code = 200 if status["status"] == "healthy" else 500
            return jsonify(status), code

        @self.api.get("/celery", summary="Celery detailed health check")
        def celery_health_check():
            status = {
                "status": "healthy",
                "celery": {
                    "workers": "unknown",
                    "broker": "unknown",
                    "task_test": "unknown",
                },
            }

            # Check Celery workers
            try:
                inspect = celery.control.inspect()
                active_workers = inspect.active()

                if active_workers:
                    worker_count = len(active_workers)
                    status["celery"]["workers"] = f"UP ({worker_count} workers active)"
                else:
                    status["celery"]["workers"] = "DOWN (no active workers)"
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Celery workers check failed: {str(e)}")
                status["celery"]["workers"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            # Check Celery broker
            try:
                connection = celery.connection()
                connection.connect()
                connection.release()
                status["celery"]["broker"] = "UP"
            except Exception as e:
                self.logger.error(f"Celery broker check failed: {str(e)}")
                status["celery"]["broker"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            # Test Celery task execution (using test_database_task)
            try:
                result = test_database_task.delay()
                result_value = result.get(timeout=10)

                if result_value.get("status") == "success":
                    status["celery"]["task_test"] = "UP"
                else:
                    status["celery"]["task_test"] = "DOWN"
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Celery task test failed: {str(e)}")
                status["celery"]["task_test"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            code = 200 if status["status"] == "healthy" else 500
            return jsonify(status), code

        @self.api.get("/database", summary="Database health check")
        def database_health_check():
            status = {
                "status": "healthy",
                "database": {
                    "connection": "unknown",
                    "query_test": "unknown",
                },
            }

            # Check database connection
            try:
                db_connected = MyDb.check_db_connection()
                status["database"]["connection"] = "UP" if db_connected else "DOWN"
                if not db_connected:
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Database connection check failed: {str(e)}")
                status["database"]["connection"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            # Test database query
            try:
                result = MyDb.check_db_execution()
                if result:
                    status["database"]["query_test"] = "UP"
                else:
                    status["database"]["query_test"] = "DOWN"
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Database query test failed: {str(e)}")
                status["database"]["query_test"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            code = 200 if status["status"] == "healthy" else 500
            return jsonify(status), code
