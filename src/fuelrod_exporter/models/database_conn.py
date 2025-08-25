import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, text
from sqlalchemy.exc import OperationalError

load_dotenv(verbose=True)


class MyDb:
    db = None
    db_url: str = os.getenv("DB_URL")
    db_schema: str = os.getenv("DB_SCHEMA", "public")  # Default to 'public'
    debug_db = os.getenv('DEBUG_DB') == '1'

    @classmethod
    def init_app(cls, app: Flask):
        # Configure database URI
        app.config["SQLALCHEMY_DATABASE_URI"] = cls.db_url

        # Set a global schema for all models
        metadata = MetaData(schema=cls.db_schema)
        cls.db = SQLAlchemy(app, metadata=metadata)

    @classmethod
    def get_db(cls):
        if cls.db is None:
            raise RuntimeError("Database is not initialized. Call init_app() with a Flask app first.")
        return cls.db

    @classmethod
    def check_db_connection(cls):
        if cls.db is None:
            raise RuntimeError("Database is not initialized.")

        try:
            connection = cls.db.session()
            connection.execute(text("SELECT 1"))
            connection.close()
            return True
        except OperationalError:
            return False
