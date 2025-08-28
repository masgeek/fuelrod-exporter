import os
from dotenv import load_dotenv
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend

# Load env vars
load_dotenv()

# Create Redis-backed result store
result_backend = RedisBackend(url=f"redis://:{os.getenv('BROKER_PASS')}@{os.getenv('BROKER_HOST')}:{os.getenv('BROKER_PORT')}/1")

# Create broker
broker = RedisBroker(
    url=f"redis://:{os.getenv('BROKER_PASS')}@{os.getenv('BROKER_HOST')}:{os.getenv('BROKER_PORT')}/{os.getenv('BROKER_DB')}"
)

# Add Results middleware
broker.add_middleware(Results(backend=result_backend))

# Register broker globally
dramatiq.set_broker(broker)
