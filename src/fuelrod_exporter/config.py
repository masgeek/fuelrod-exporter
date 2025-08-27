import os

from dotenv import load_dotenv

load_dotenv(verbose=True)


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_NAME = os.getenv("APP_NAME", "Fuelrod Exporter")
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
    API_PREFIX = os.getenv("API_PREFIX", "/api")
