# fuelrod_exporter/app.py

import os
from dotenv import load_dotenv
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Server, Contact, License, Info

from fuelrod_exporter.api.v1.routes import v1_blueprints
from fuelrod_exporter.config import Config
from fuelrod_exporter.core.database import MyDb

load_dotenv()

contact = Contact(
    name="Munywele Consulting LTD",
    email="dev@munywele.co.ke",
    url="https://munywele.co.ke"
)

api_license = License(
    name="Apache 2.0",
    identifier="Apache-2.0"
)

info = Info(
    title=Config.APP_NAME,
    version=Config.APP_VERSION,
    contact=contact,
    license=api_license,
    termsOfService=Config.TERMS_OF_SERVICE_URL
)

servers = [
    Server(url=f"http://127.0.0.1:{Config.SERVER_PORT}"),
    Server(url=os.getenv("SERVER_URL_PROD", "https://export.munywele.co.ke")),
]


def init_db(app):
    MyDb.init_app(app)


# **Singleton app instance**
_app = None


def get_app():
    global _app
    if _app is None:
        app = OpenAPI(
            __name__,
            servers=servers,
            info=info,
            security_schemes={
                "basic": {"type": "http", "scheme": "basic"},
                "jwt": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            }
        )
        CORS(app)
        app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
        app.config["SQLALCHEMY_ECHO"] = Config.DEBUG_DB
        app.json.sort_keys = Config.SORT_JSON
        init_db(app)
        for bp in v1_blueprints:
            app.register_api(bp)

        scheduler = APScheduler()
        scheduler.api_enabled = Config.SCHEDULER_API_ENABLED
        # 🔁 Register jobs explicitly
        for job in Config.SCHEDULER_JOBS:
            scheduler.add_job(**job)

        scheduler.init_app(app)
        scheduler.start()
        _app = app
    return _app
