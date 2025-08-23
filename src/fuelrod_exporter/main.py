"""
Simple test runner for generated ORM models using db.py.
"""

from sqlalchemy import text
from fuelrod_exporter.db import get_session, engine, DB_SCHEMA
from fuelrod_exporter.models import SmsOutbox


def test_connection():
    """Verify database connection and active schema."""
    with engine.connect() as conn:
        # Ensure schema is set explicitly
        conn.execute(text(f"SET search_path TO {DB_SCHEMA}"))
        result = conn.execute(text("SELECT current_schema()")).scalar_one()
        print(f"Connected. Current schema: {result}")


def test_query():
    """Try querying the SmsOutbox model if it exists."""
    session = get_session()
    try:
        rows = session.query(SmsOutbox).limit(5).all()
        print(f"Found {len(rows)} rows in SmsOutbox:")
        for row in rows:
            print(f"- message_id={row.message_id}, phone_number={row.phone_number}")
    finally:
        session.close()


if __name__ == "__main__":
    test_connection()
    # Uncomment to test query against SmsOutbox
    # test_query()
