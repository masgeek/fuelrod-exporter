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
    SERVER_URL_PROD = os.getenv("SERVER_URL_PROD", "https://export.munywele.co.ke")
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
    API_PREFIX = os.getenv("API_PREFIX", "/api")
    TERMS_OF_SERVICE_URL = os.getenv("TERMS_OF_SERVICE_URL", "https://munywele.co.ke/terms-of-service")

    SERVER_TZ = os.getenv("TIMEZONE", "Africa/Nairobi")
    EXPORT_FOLDER = os.getenv("EXPORT_FOLDER", "exports")
    API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{SERVER_PORT}")

    BROKER_PASS = os.getenv("BROKER_PASS")
    BROKER_PORT = os.getenv("BROKER_PORT", 6379)
    BROKER_DB = os.getenv("BROKER_DB", 0)
    RESULT_DB = os.getenv("RESULT_DB", 1)
    BROKER_HOST = os.getenv("BROKER_HOST", "127.0.0.1")
    BROKER_SERVICE = os.getenv("BROKER_SERVICE", "redis")

    # Fixed URL building with proper password handling
    @classmethod
    def _build_redis_url(cls, db):
        """Build Redis URL with proper password handling."""
        if cls.BROKER_PASS:
            return f"{cls.BROKER_SERVICE}://:{cls.BROKER_PASS}@{cls.BROKER_HOST}:{cls.BROKER_PORT}/{db}"
        else:
            return f"{cls.BROKER_SERVICE}://{cls.BROKER_HOST}:{cls.BROKER_PORT}/{db}"

    @property
    def CELERY_BROKER_URL(self):
        return self._build_redis_url(self.BROKER_DB)

    @property
    def CELERY_RESULT_BACKEND(self):
        return self._build_redis_url(self.RESULT_DB)

    @property
    def REDIS_URL(self):
        return self._build_redis_url(self.BROKER_DB)

    CELERY_REDIS_MAX_CONNECTIONS = os.getenv("CELERY_REDIS_MAX_CONNECTIONS", 10)