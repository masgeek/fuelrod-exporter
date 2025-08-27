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
    debug_db = os.getenv("DEBUG_DB") == "1"

    @classmethod
    def init_app(cls, app: Flask):
        """Initialize SQLAlchemy with custom schema and config."""
        app.config["SQLALCHEMY_DATABASE_URI"] = cls.db_url

        metadata = MetaData(schema=cls.db_schema)
        cls.db = SQLAlchemy(app, metadata=metadata)

    @classmethod
    def get_db(cls):
        if cls.db is None:
            raise RuntimeError(
                "Database is not initialized. Call init_app() with a Flask app first."
            )
        return cls.db

    @classmethod
    def check_db_connection(cls) -> bool:
        """Return True if DB is reachable, False otherwise."""
        if cls.db is None:
            raise RuntimeError("Database is not initialized.")

        try:
            with cls.db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except OperationalError:
            return False

    @classmethod
    def _get_table_count(cls) -> int:
        """Return the number of tables in the current schema."""
        if cls.db is None:
            raise RuntimeError("Database is not initialized.")

        try:
            insp = cls.db.inspect(cls.db.engine)
            tables = insp.get_table_names(schema=cls.db_schema)
            return len(tables)
        except Exception as e:
            raise RuntimeError(f"Error retrieving table count: {e}")

    @classmethod
    def get_db_details(cls) -> dict:
        """Return database connection details (engine, schema, version, etc.)."""
        if cls.db is None:
            raise RuntimeError("Database is not initialized.")

        try:
            with cls.db.engine.connect() as conn:
                insp = cls.db.inspect(cls.db.engine)

                details = {
                    "connected": True,
                    "dialect": cls.db.engine.url.get_dialect().name,
                    "driver": cls.db.engine.url.drivername,
                    "schema": cls.db_schema,
                    # "server_version": conn.exec_driver_sql("SELECT version()").scalar(),
                    "schemas_available": insp.get_schema_names(),
                    "table_count": cls._get_table_count(),
                    "tables": insp.get_table_names(schema=cls.db_schema),
                    "view_count": len(insp.get_view_names(schema=cls.db_schema)),
                    "views": insp.get_view_names(schema=cls.db_schema),
                }

                # Postgres-only extras
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

