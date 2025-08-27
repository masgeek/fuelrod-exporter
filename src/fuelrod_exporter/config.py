import os

from dotenv import load_dotenv

load_dotenv(verbose=True)


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_DB = os.getenv("DEBUG_DB") == "1"
    SORT_JSON = os.getenv("SORT_JSON") == "1"

    APP_NAME = os.getenv("APP_NAME", "Fuelrod Exporter")
    SERVER_PORT = os.getenv("SERVER_PORT", 3000)
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
    API_PREFIX = os.getenv("API_PREFIX", "/api")
    TERMS_OF_SERVICE_URL = os.getenv("TERMS_OF_SERVICE_URL", "https://munywele.co.ke/terms-of-service")
