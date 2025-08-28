import logging

from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

from fuelrod_exporter.config import Config
from fuelrod_exporter.core.database import MyDb
from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.tasks.system_tasks import ping


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
                    "celery": "unknown"
                }
            }

            # Check DB
            try:
                db_connected = MyDb.check_db_connection()
                status["components"]["database"] = "UP" if db_connected else "DOWN"
                if not db_connected:
                    status["status"] = "degraded"
            except Exception as e:
                status["components"]["database"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            # Check Celery
            try:
                result = ping.delay()
                result_value = result.get(timeout=5)
                if result_value == "pong":
                    status["components"]["celery"] = "UP"
                else:
                    status["components"]["celery"] = "UNRESPONSIVE"
                    status["status"] = "degraded"
            except Exception as e:
                status["components"]["celery"] = f"ERROR: {str(e)}"
                status["status"] = "degraded"

            code = 200 if status["status"] == "healthy" else 500
            return jsonify(status), code
