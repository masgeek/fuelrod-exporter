import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend
from dramatiq.middleware import Middleware
from fuelrod_exporter.config import Config

result_backend = RedisBackend(url=Config.RESULT_BACKEND)


broker = RedisBroker(url=Config.BROKER_URL)

broker.add_middleware(Results(backend=result_backend))

dramatiq.set_broker(broker)
