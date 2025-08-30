import logging
from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

from fuelrod_exporter.config import Config
from fuelrod_exporter.core.database import MyDb
from fuelrod_exporter.core.logging import SharedLogger
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
        self.logger = SharedLogger().get_logger()

        # Register routes
        self._register_routes()

    def _register_routes(self):
        @self.api.get("/", summary="Combined health check")
        def health_check():
            status = {
                "status": "healthy",
                "components": {
                    "database": "unknown",
                    "dramatiq": "unknown",
                },
            }

            # ✅ Database check
            try:
                db_connected = MyDb.check_db_connection()
                status["components"]["database"] = "UP" if db_connected else "DOWN"
                if not db_connected:
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Database health check failed: {str(e)}")
                status["components"]["database"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            # ✅ Dramatiq check (submit a test job)
            try:
                future = test_database_task.send()
                result_value = future.get_result(block=True, timeout=30)

                if result_value.get("status") == "success":
                    status["components"]["dramatiq"] = "UP"
                else:
                    status["components"]["dramatiq"] = "DOWN"
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Dramatiq health check failed: {str(e)}")
                status["components"]["dramatiq"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            code = 200 if status["status"] == "healthy" else 500
            return jsonify(status), code

        @self.api.get("/dramatiq", summary="Dramatiq detailed health check")
        def dramatiq_health_check():
            status = {
                "status": "healthy",
                "dramatiq": {
                    "workers": "N/A",   # dramatiq doesn’t expose active worker inspection like Celery
                    "broker": "unknown",
                    "task_test": "unknown",
                },
            }

            # ✅ Check broker (Ping via test task)
            try:
                future = health_check_task.send()
                result_value = future.get_result(block=True, timeout=10)

                if result_value.get("status") == "ok":
                    status["dramatiq"]["broker"] = "UP"
                else:
                    status["dramatiq"]["broker"] = "DOWN"
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Dramatiq broker check failed: {str(e)}")
                status["dramatiq"]["broker"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            # ✅ Test Dramatiq task execution
            try:
                future = test_database_task.send()
                result_value = future.get_result(block=True, timeout=10)

                if result_value.get("status") == "success":
                    status["dramatiq"]["task_test"] = "UP"
                else:
                    status["dramatiq"]["task_test"] = "DOWN"
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Dramatiq task test failed: {str(e)}")
                status["dramatiq"]["task_test"] = f"ERROR: {str(e)}"
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

            # ✅ Connection check
            try:
                db_connected = MyDb.check_db_connection()
                status["database"]["connection"] = "UP" if db_connected else "DOWN"
                if not db_connected:
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Database connection check failed: {str(e)}")
                status["database"]["connection"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            # ✅ Query test
            try:
                result = MyDb.check_db_execution()
                status["database"]["query_test"] = "UP" if result else "DOWN"
                if not result:
                    status["status"] = "degraded"
            except Exception as e:
                self.logger.error(f"Database query test failed: {str(e)}")
                status["database"]["query_test"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            code = 200 if status["status"] == "healthy" else 500
            return jsonify(status), code
