# fuelrod_exporter/core/celery.py

from celery import Celery
from fuelrod_exporter.config import Config

def build_redis_url(host, port, password, db):
    """Build Redis URL with proper password handling."""
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    else:
        return f"redis://{host}:{port}/{db}"

# Create Celery instance
my_celery = Celery('fuelrod_exporter')

# Build proper Redis URLs
broker_url = build_redis_url(
    Config.BROKER_HOST, 
    Config.BROKER_PORT, 
    Config.BROKER_PASS, 
    Config.BROKER_DB
)

result_backend = build_redis_url(
    Config.BROKER_HOST, 
    Config.BROKER_PORT, 
    Config.BROKER_PASS, 
    Config.RESULT_DB
)

# Configure Celery with your settings
celery_config = {
    'broker_url': broker_url,
    'result_backend': result_backend,
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': Config.SERVER_TZ,
    'enable_utc': True,
    'broker_connection_retry_on_startup': True,
    'broker_connection_retry': True,
    'broker_connection_max_retries': 10,
    'redis_max_connections': int(Config.CELERY_REDIS_MAX_CONNECTIONS),
    'task_track_started': True,
    'task_time_limit': 30 * 60,  # 30 minutes
    'task_soft_time_limit': 25 * 60,  # 25 minutes
    'worker_prefetch_multiplier': 1,
    'worker_max_tasks_per_child': 1000,
    # Task routing
    'task_routes': {
        'system.*': {'queue': 'system'},
    },
}

my_celery.conf.update(celery_config)

# Auto-discover tasks
my_celery.autodiscover_tasks([
    'fuelrod_exporter.tasks',
    'fuelrod_exporter.api.v1.controllers',
])