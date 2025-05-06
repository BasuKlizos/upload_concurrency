import os
import dramatiq

from dotenv import load_dotenv
from dramatiq.brokers.redis import RedisBroker

load_dotenv()

REDIS_URL = os.getenv("DRAMATIQ_BROKER_URL", "redis://localhost:6379/0")

# broker = RedisBroker(url=REDIS_URL)
# dramatiq.set_broker(broker)
