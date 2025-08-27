from flask import redirect, jsonify

from fuelrod_exporter.core.database import MyDb


def register_app_routes(app):
    """
    Register routes for the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """

    @app.route('/')
    def index():
        """
        Route for the root URL.

        Returns:
            Response: Redirect to /openapi/swagger.
        """
        return redirect('/openapi')

    @app.route('/health', methods=['GET'])
    def health_check():
        db_connected = MyDb.check_db_connection()

        health_status = {
            "status": "healthy" if db_connected else "unhealthy",
            "database": "UP" if db_connected else "DOWN"
        }
        return jsonify(health_status), 200 if db_connected else 500
