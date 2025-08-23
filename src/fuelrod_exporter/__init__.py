from flask import Flask
from .db import create_engine
from .app import register_routes


def create_app():
    app = Flask(__name__)

    # Load DB + routes
    init_db()
    register_routes(app)

    return app
