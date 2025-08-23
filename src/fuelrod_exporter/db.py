"""
Database setup: engine, session, and base imports.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

DB_URL = os.getenv("DB_URL")
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")
DEBUG_DB = os.getenv("DEBUG_DB") == "1"

if not DB_URL:
    raise RuntimeError("DB_URL environment variable is not set in .env")

# SQLAlchemy engine & session
engine = create_engine(DB_URL, echo=DEBUG_DB, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session(schema: str = None):
    """
    Returns an SQLAlchemy session with search_path set to the given schema.
    Defaults to DB_SCHEMA from environment.
    """
    schema = schema or DB_SCHEMA
    session = SessionLocal()
    session.execute(text(f"SET search_path TO {schema}"))
    return session


def test_connection(schema: str = None):
    """
    Verifies DB connection and schema.
    """
    schema = schema or DB_SCHEMA
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_schema()")).scalar_one()
        print(f"✅ Connected. Current schema: {result} (expected {schema})")
