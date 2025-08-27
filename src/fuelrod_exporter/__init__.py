import os

from dotenv import load_dotenv
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Server, Contact, License, Info

from fuelrod_exporter.core.database import MyDb
from fuelrod_exporter.api.v1.routes import v1_blueprints
from fuelrod_exporter.api.v1.controllers.report_controller import ReportsController
from fuelrod_exporter.config import Config

# Load environment variables from .env file
load_dotenv()

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
    title=Config.APP_NAME,
    version=Config.APP_VERSION,
    contact=contact,
    license=api_license,
    termsOfService=Config.TERMS_OF_SERVICE_URL
)

# API servers
servers = [
    Server(url=f"http://127.0.0.1:{Config.SERVER_PORT}"),
    Server(url=os.getenv("SERVER_URL_PROD", "https://export.munywele.co.ke")),
]


def init_db(app):
    """Initialize the database with the Flask app."""
    MyDb.init_app(app)


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
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_ECHO'] = Config.DEBUG_DB
    app.json.sort_keys = Config.SORT_JSON

    # Initialize the database
    init_db(app)

    # Register APIs and other routes
    for bp in v1_blueprints:
        print(bp)
        app.register_api(bp)

    return app
