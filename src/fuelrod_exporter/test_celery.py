#!/usr/bin/env python3
"""
Test script to verify Celery connection with your specific configuration.
Run this to check if Celery connects properly.
"""

import os
import sys
from dotenv import load_dotenv
from fuelrod_exporter.core.celery import my_celery as celery
from fuelrod_exporter import create_app  # Adjust this import to match your main app file
import redis
from fuelrod_exporter.config import Config
from fuelrod_exporter.tasks.system_tasks import health_check_task, test_database_task

# Load environment variables
load_dotenv()


def test_redis_connection():
    """Test Redis connection directly using your config."""
    print("=== Testing Redis Connection ===")

    try:
        def build_redis_url(db):
            if Config.BROKER_PASS:
                return f"redis://:{Config.BROKER_PASS}@{Config.BROKER_HOST}:{Config.BROKER_PORT}/{db}"
            else:
                return f"redis://{Config.BROKER_HOST}:{Config.BROKER_PORT}/{db}"

        broker_url = build_redis_url(Config.BROKER_DB)
        result_url = build_redis_url(Config.RESULT_DB)

        print("Config values:")
        print(f"  BROKER_HOST: {Config.BROKER_HOST}")
        print(f"  BROKER_PORT: {Config.BROKER_PORT}")
        print(f"  BROKER_PASS: {'***' if Config.BROKER_PASS else 'None'}")
        print(f"  BROKER_DB: {Config.BROKER_DB}")
        print(f"  RESULT_DB: {Config.RESULT_DB}")
        print(f"  Broker URL: {broker_url}")
        print(f"  Result URL: {result_url}")

        # Test broker connection
        print("\nTesting broker connection...")
        r_broker = redis.from_url(broker_url)
        r_broker.ping()
        print("✓ Broker Redis connection successful")

        # Test result backend connection
        print("Testing result backend connection...")
        r_result = redis.from_url(result_url)
        r_result.ping()
        print("✓ Result backend Redis connection successful")

        # Test operations
        r_broker.set('test_key', 'test_value')
        value = r_broker.get('test_key')
        print(f"✓ Redis read/write test: {value.decode() if value else None}")
        r_broker.delete('test_key')

    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        import traceback
        traceback.print_exc()


def test_celery_standalone():
    """Test Celery configuration standalone."""
    print("\n=== Testing Celery Standalone ===")

    try:
        print(f"Celery broker URL: {celery.conf.broker_url}")
        print(f"Celery result backend: {celery.conf.result_backend}")
        print(f"Celery timezone: {celery.conf.timezone}")

        # Test connection
        connection = celery.connection()
        connection.connect()
        print("✓ Celery broker connection successful")
        connection.release()

        # Test worker inspection
        inspect = celery.control.inspect()
        active_workers = inspect.active()
        if active_workers:
            print(f"✓ Found {len(active_workers)} active workers")
            for worker, tasks in active_workers.items():
                print(f"  - {worker}: {len(tasks)} active tasks")
        else:
            print("ℹ No active workers found (this is normal if no workers are running)")

    except Exception as e:
        print(f"✗ Celery standalone test failed: {e}")
        import traceback
        traceback.print_exc()


def test_celery_task():
    """Test Celery health check task."""
    print("\n=== Testing Celery Health Check Task ===")

    try:
        print("Submitting health check task...")
        result = health_check_task.delay()
        print(f"Task ID: {result.id}")

        print("Waiting for result...")
        response = result.get(timeout=10)
        print(f"✓ Health check completed successfully: {response}")

    except Exception as e:
        print(f"✗ Health check task failed: {e}")
        print("Make sure you have a Celery worker running:")
        print("  celery -A fuelrod_exporter.core.celery:my_celery worker --loglevel=info")


def test_database_via_celery():
    """Test database connectivity via Celery worker task."""
    print("\n=== Testing Database Connectivity via Celery ===")

    try:
        print("Submitting database test task...")
        result = test_database_task.delay()
        print(f"Task ID: {result.id}")

        print("Waiting for result...")
        response = result.get(timeout=10)
        print(f"✓ Database test completed: {response}")

    except Exception as e:
        print(f"✗ Database test task failed: {e}")


def test_flask_celery():
    """Test Celery within Flask app context."""
    print("\n=== Testing Flask App Celery ===")

    try:
        sys.path.append('.')
        app = create_app()

        with app.app_context():
            print(f"Flask context Celery broker: {celery.conf.broker_url}")
            print(f"Flask context Celery result backend: {celery.conf.result_backend}")

            # Test connection within Flask context
            connection = celery.connection()
            connection.connect()
            print("✓ Celery connection successful within Flask context")
            connection.release()

            # Test health check task within Flask context
            result = health_check_task.delay()
            response = result.get(timeout=10)
            print(f"✓ Health check successful in Flask context: {response}")

            # Test database task within Flask context
            result_db = test_database_task.delay()
            response_db = result_db.get(timeout=10)
            print(f"✓ Database test successful in Flask context: {response_db}")

    except ImportError as e:
        print(f"Cannot import Flask app: {e}")
        print("Adjust the import in this script to match your main app file")
    except Exception as e:
        print(f"✗ Flask Celery test failed: {e}")


def main():
    """Run all tests."""
    print("Celery Configuration Test Script")
    print("=" * 50)

    print("Environment variables:")
    env_vars = [
        'BROKER_HOST', 'BROKER_PORT', 'BROKER_PASS', 'BROKER_DB',
        'RESULT_DB', 'BROKER_SERVICE', 'CELERY_REDIS_MAX_CONNECTIONS'
    ]

    for var in env_vars:
        value = os.getenv(var)
        if var == 'BROKER_PASS' and value:
            value = '***'  # Hide password
        print(f"  {var}: {value if value else 'NOT SET'}")

    print("\n" + "=" * 50)

    test_redis_connection()
    test_celery_standalone()
    test_celery_task()
    test_database_via_celery()
    test_flask_celery()

    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nIf tests fail:")
    print("1. Make sure Redis is running: redis-server")
    print("2. Check your .env file has correct values")
    print("3. Start a Celery worker: celery -A fuelrod_exporter.core.celery:my_celery worker --loglevel=info")


if __name__ == '__main__':
    main()
