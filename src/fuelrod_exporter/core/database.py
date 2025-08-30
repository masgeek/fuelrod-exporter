import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, text
from sqlalchemy.exc import OperationalError

from fuelrod_exporter.config import Config

load_dotenv(verbose=True)

# Create the SQLAlchemy instance ONCE (no app bound yet)
metadata = MetaData(schema=Config.DB_SCHEMA)
db = SQLAlchemy(metadata=metadata)


class MyDb:
    db_url: str = Config.SQLALCHEMY_DATABASE_URI
    db_schema: str = Config.DB_SCHEMA

    @classmethod
    def init_app(cls, app: Flask):
        """Configure SQLAlchemy once"""
        if "sqlalchemy" not in app.extensions:  # 🚑 prevent double registration
            app.config["SQLALCHEMY_DATABASE_URI"] = cls.db_url
            db.init_app(app)

    @classmethod
    def get_db(cls):
        return db

    @classmethod
    def check_db_connection(cls) -> bool:
        """Return True if DB is reachable, False otherwise."""
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except OperationalError:
            return False

    @classmethod
    def check_db_execution(cls):
        with db.engine.connect() as conn:
            return conn.execute(text("SELECT 1")).fetchone()

    @classmethod
    def _get_table_count(cls) -> int:
        """Return the number of tables in the current schema."""
        try:
            insp = db.inspect(db.engine)
            tables = insp.get_table_names(schema=cls.db_schema)
            return len(tables)
        except Exception as e:
            raise RuntimeError(f"Error retrieving table count: {e}")

    @classmethod
    def get_db_details(cls) -> dict:
        """Return database connection details (engine, schema, version, etc.)."""
        try:
            with db.engine.connect() as conn:
                insp = db.inspect(db.engine)

                details = {
                    "connected": True,
                    "dialect": db.engine.url.get_dialect().name,
                    "driver": db.engine.url.drivername,
                    "schema": cls.db_schema,
                    "schemas_available": insp.get_schema_names(),
                    "table_count": cls._get_table_count(),
                    "tables": insp.get_table_names(schema=cls.db_schema),
                    "view_count": len(insp.get_view_names(schema=cls.db_schema)),
                    "views": insp.get_view_names(schema=cls.db_schema),
                }

                if details["dialect"] == "postgresql":
                    details["current_database"] = conn.exec_driver_sql(
                        "SELECT current_database()"
                    ).scalar()
                    details["current_user"] = conn.exec_driver_sql(
                        "SELECT current_user"
                    ).scalar()
                    details["database_size"] = conn.exec_driver_sql(
                        "SELECT pg_size_pretty(pg_database_size(current_database()))"
                    ).scalar()

                return details

        except OperationalError as e:
            return {
                "connected": False,
                "error": str(e.__cause__ or e),
                "url": cls.db_url,
                "schema": cls.db_schema,
            }
