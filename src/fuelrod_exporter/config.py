"""
Configuration settings for FuelRod Exporter
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Application configuration"""

    # Database Configuration
    MYSQL_HOST: str = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT: int = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_USER: str = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD: str = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE: str = os.getenv('MYSQL_DATABASE', 'fuelrod_db')

    # PostgreSQL Configuration (alternative)
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT: int = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', '')
    POSTGRES_DATABASE: str = os.getenv('POSTGRES_DATABASE', 'fuelrod_db')

    # Redis Configuration
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB: int = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD', '')

    # Flask Configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    # Export Configuration
    EXPORT_CHUNK_SIZE: int = int(os.getenv('EXPORT_CHUNK_SIZE', '10000'))
    MAX_EXPORT_RECORDS: int = int(os.getenv('MAX_EXPORT_RECORDS', '1000000'))
    EXPORT_TIMEOUT: int = int(os.getenv('EXPORT_TIMEOUT', '3600'))  # 1 hour
    TEMP_DIR: str = os.getenv('TEMP_DIR', '/tmp/fuelrod_exports')

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/fuelrod.log')

    # API Configuration
    API_PREFIX: str = os.getenv('API_PREFIX', '/api/v1')
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')

    # Performance Configuration
    MAX_WORKERS: int = int(os.getenv('MAX_WORKERS', '4'))

    @property
    def database_url(self) -> str:
        """Get database URL based on database type"""
        db_type = os.getenv('DATABASE_TYPE', 'postgresql').lower()

        if db_type == 'postgresql':
            return (f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                    f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")
        else:  # Default to MySQL
            return (f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                    f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}")


# Global config instance
config = Config()


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    MYSQL_DATABASE = 'fuelrod_test_db'
    POSTGRES_DATABASE = 'fuelrod_test_db'
    REDIS_DB = 1


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development').lower()

    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()