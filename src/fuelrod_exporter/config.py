import os

from dotenv import load_dotenv

load_dotenv(verbose=True)


class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL")
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

    # Server
    SERVER_TZ = os.getenv("TIMEZONE", "Africa/Nairobi")
    EXPORT_FOLDER = os.getenv("EXPORT_FOLDER", "exports")
    API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{os.getenv('SERVER_PORT', 3000)}")

    # Redis / Celery
    BROKER_PASS = os.getenv("BROKER_PASS")
    BROKER_PORT = int(os.getenv("BROKER_PORT", 6379))
    BROKER_DB = int(os.getenv("BROKER_DB", 0))
    RESULT_DB = int(os.getenv("RESULT_DB", 3))
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
