import os

from dotenv import load_dotenv
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Server, Contact, License, Info

from fuelrod_exporter.core.database_conn import MyDb
from fuelrod_exporter.api.v1.main import register_app_routes
from . import config

# Load environment variables from .env file
load_dotenv()

port = os.getenv('SERVER_PORT', default=3000)

# API contact information
contact = Contact(
    name="Munywele Consulting LTD",
    email="dev@munywele.co.ke",
    url="https://munywele.co.ke"
)

# API license information
api_license = License(
    name="Apache 2.0",
    identifier="Apache-2.0"
)

# API information
info = Info(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    contact=contact,
    license=api_license,
    termsOfService="https://munywele.co.ke/terms-of-service"
)

# API servers
servers = [
    Server(url=f"http://127.0.0.1:{port}"),
    Server(url=os.getenv("SERVER_URL_PROD", "https://export.munywele.co.ke")),
]


def init_db(app):
    """Initialize the database with the Flask app."""
    MyDb.init_app(app)


def register_apis(app: OpenAPI):
    """Register all API Blueprints with the Flask app."""
    from fuelrod_exporter.api.v1.controllers.user_controller import api as user_api
    from fuelrod_exporter.api.v1.controllers.report_controller import api as report_api

    app.register_api(user_api)
    app.register_api(report_api)


def create_app():
    """Create and configure the Flask app."""
    app = OpenAPI(
        __name__,
        servers=servers,
        info=info,
        security_schemes={
            "basic": {"type": "http", "scheme": "basic"},
            "jwt": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }
    )

    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app)

    # Configure the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
    app.config['SQLALCHEMY_ECHO'] = os.getenv('DEBUG_DB') == '1'
    app.json.sort_keys = os.getenv('SORT_JSON') == '1'

    # Initialize the database
    init_db(app)

    # Register APIs and other routes
    register_apis(app)
    register_app_routes(app)

    return app
