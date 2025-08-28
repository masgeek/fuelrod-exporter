# fuelrod_exporter/worker_app.py
from flask import Flask
from fuelrod_exporter.config import Config
from fuelrod_exporter.core.database import MyDb

_app = None

def get_app():
    global _app
    if _app is None:
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
        app.config["SQLALCHEMY_ECHO"] = Config.DEBUG_DB
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        MyDb.init_app(app)
        _app = app
    return _app
