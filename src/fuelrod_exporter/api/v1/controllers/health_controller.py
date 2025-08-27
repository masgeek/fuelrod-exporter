import logging

from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag

from fuelrod_exporter.config import Config
from fuelrod_exporter.core.database import MyDb
from fuelrod_exporter.core.logging import SharedLogger


class HealthController:
    __bp__ = "/health"

    def __init__(self):
        # Setup URL prefix
        url_prefix = Config.API_PREFIX + self.__bp__

        # Setup tags & blueprint
        tag = Tag(name="fuelrod", description="Health check")
        self.api = APIBlueprint(
            self.__bp__, __name__, url_prefix=url_prefix, abp_tags=[tag]
        )
        # Repo & logger
        self.logger = SharedLogger(level=logging.DEBUG).get_logger()
        # Register routes

    def _register_routes(self):
        @self.api.get("/")
        def health_check():
            """
            Basic health check.
            Optionally pings DB to verify connectivity.
            """
            try:
                db_connected = MyDb.check_db_connection()
                health_status = {
                    "status": "healthy" if db_connected else "unhealthy",
                    "db": "UP" if db_connected else "DOWN"
                }
                return jsonify(health_status), 200 if db_connected else 500
            except Exception as e:
                return jsonify({"status": "degraded", "db": str(e)}), 500
