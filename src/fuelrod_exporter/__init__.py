import os

from dotenv import load_dotenv
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Server, Contact, License, Info

from fuelrod_exporter.core.database import MyDb
from fuelrod_exporter.core.celery import my_celery as celery
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


def init_celery(app, celery_app):
    """Initialize Celery with the Flask app context."""

    # Get config instance

    # Build Redis URLs properly
    def build_redis_url(db):
        if Config.BROKER_PASS:
            return f"{Config.BROKER_SERVICE}://:{Config.BROKER_PASS}@{Config.BROKER_HOST}:{Config.BROKER_PORT}/{db}"
        else:
            return f"{Config.BROKER_SERVICE}://{Config.BROKER_HOST}:{Config.BROKER_PORT}/{db}"

    broker_url = build_redis_url(Config.BROKER_DB)
    result_backend = build_redis_url(Config.RESULT_DB)

    # Update Celery configuration with Flask app config
    celery_app.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone=Config.SERVER_TZ,
        enable_utc=True,
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10,
        redis_max_connections=int(Config.CELERY_REDIS_MAX_CONNECTIONS),
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )

    # Ensure tasks run within Flask app context
    class ContextTask(celery_app.Task):
        """Make celery tasks work with Flask app context."""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask

    # Force reload configuration
    try:
        celery_app.loader.init_worker_process()
    except AttributeError:
        # Some Celery versions don't have this method
        pass

    return celery_app


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

    # Add Celery configuration to Flask config (for consistency)

    app.config['CELERY_BROKER_URL'] = Config.CELERY_BROKER_URL
    app.config['CELERY_RESULT_BACKEND'] = Config.CELERY_RESULT_BACKEND

    # Initialize the database
    init_db(app)

    # Initialize Celery with Flask app context
    init_celery(app, celery)

    # print(app.config)

    # Initialize the database
    init_db(app)

    # Register APIs and other routes
    for bp in v1_blueprints:
        print(bp)
        app.register_api(bp)

    return app


def create_celery_app():
    """Create a Celery app for running workers."""
    flask_app = create_app()
    return celery
