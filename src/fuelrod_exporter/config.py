import os
import re

from dotenv import load_dotenv

from fuelrod_exporter.core.logging import SharedLogger
from fuelrod_exporter.utils import parse_interval_to_seconds, parse_env_list

load_dotenv(verbose=True)

logger = SharedLogger().get_logger()
REQUIRED_KEYS = [
    "DB_USERNAME",
    "DB_PASSWORD",
    "MINIO_ACCESS_KEY",
    "MINIO_SECRET_KEY"
]

missing = [key for key in REQUIRED_KEYS if not os.getenv(key)]
if missing:
    message = "Missing required environment variables: " + ", ".join(missing)
    logger.critical(message)
    raise EnvironmentError(message)


class Config:
    # Database
    DB_DRIVER = os.getenv("DB_DRIVER", "postgresql")
    DB_USER = os.getenv("DB_USERNAME", "pguser")
    DB_PASS = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_DATABASE", "postgres")
    DB_SCHEMA = os.getenv("DB_SCHEMA", "public")

    if DB_PASS:
        SQLALCHEMY_DATABASE_URI = f"{DB_DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        SQLALCHEMY_DATABASE_URI = f"{DB_DRIVER}://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_DB = os.getenv("DEBUG_DB") == "1"
    SORT_JSON = os.getenv("SORT_JSON") == "1"

    # App metadata
    APP_NAME = os.getenv("APP_NAME", "Fuelrod Exporter")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 3000))
    SERVER_URL_PROD = os.getenv("SERVER_URL_PROD", "https://export.munywele.co.ke")
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
    API_PREFIX = os.getenv("API_PREFIX", "/api")
    TERMS_OF_SERVICE_URL = os.getenv(
        "TERMS_OF_SERVICE_URL", "https://munywele.co.ke/terms-of-service"
    )

    # min io
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9005")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "fuelrod")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

    # files
    ALLOWED_EXTENSIONS = parse_env_list( os.getenv("ALLOWED_EXTENSIONS", ".csv,.json,.xlsx,.txt"))
    PROTECTED_FILES = parse_env_list(os.getenv("PROTECTED_FILES", ".gitignore"))

    # Server
    SERVER_TZ = os.getenv("TIMEZONE", "UTC")
    EXPORT_FOLDER = os.getenv("EXPORT_FOLDER", "exports")
    EXPORT_MAX_AGE = os.getenv("EXPORT_MAX_AGE", "30d")
    API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{os.getenv('SERVER_PORT', 3000)}")

    # SchedulerNotRunningError
    SCHEDULER_API_ENABLED = os.getenv("SCHEDULER_API_ENABLED", "false").lower() == "true"

    # Redis / Celery
    BROKER_PASS = os.getenv("BROKER_PASS")
    BROKER_PORT = int(os.getenv("BROKER_PORT", 6379))
    BROKER_DB = int(os.getenv("BROKER_DB", 0))
    RESULT_DB = int(os.getenv("RESULT_DB", 1))
    BROKER_HOST = os.getenv("BROKER_HOST", "127.0.0.1")
    BROKER_SERVICE = os.getenv("BROKER_SERVICE", "redis")

    BROKER_URL = (
        f"{BROKER_SERVICE}://:{BROKER_PASS}@{BROKER_HOST}:{BROKER_PORT}/{BROKER_DB}"
        if BROKER_PASS
        else f"{BROKER_SERVICE}://{BROKER_HOST}:{BROKER_PORT}/{BROKER_DB}"
    )

    RESULT_BACKEND = (
        f"{BROKER_SERVICE}://:{BROKER_PASS}@{BROKER_HOST}:{BROKER_PORT}/{RESULT_DB}"
        if BROKER_PASS
        else f"{BROKER_SERVICE}://{BROKER_HOST}:{BROKER_PORT}/{RESULT_DB}"
    )

    REDIS_URL = BROKER_URL

    raw_interval = os.getenv("SCHEDULER_INTERVAL", "24h")
    try:
        SCHEDULER_INTERVAL = parse_interval_to_seconds(raw_interval)
    except ValueError as e:
        logger.critical(str(e))
        SCHEDULER_INTERVAL = 3600

    SCHEDULER_JOBS = [
        {
            "id": "cleanup_exports",
            "func": "fuelrod_exporter.tasks.cleanup:trigger_cleanup",
            "trigger": "interval",
            "seconds": SCHEDULER_INTERVAL,
            "replace_existing": True
        }
    ]
