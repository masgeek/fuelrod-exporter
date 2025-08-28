import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend
from dramatiq.middleware import Middleware
from fuelrod_exporter.config import Config

result_backend = RedisBackend(url=Config.RESULT_BACKEND)


class NoHeartbeatMiddleware(Middleware):
    def after_process_message(self, broker, message, *, result=None, exception=None):
        pass


broker = RedisBroker(url=Config.BROKER_URL)

broker.add_middleware(NoHeartbeatMiddleware())
broker.add_middleware(Results(backend=result_backend))

dramatiq.set_broker(broker)
