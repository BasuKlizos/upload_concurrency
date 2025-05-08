import redis
from dramatiq.encoder import JSONEncoder
from dramatiq.message import Message
from backend.task_tracking.tracker import update_task_status

redis_client = redis.Redis(host="localhost", port=6379, db=0)
encoder = JSONEncoder()

def cancel_task(task_id: str, queue_name: str = "zip-file-process") -> bool:
    queue_key = f"dramatiq:{queue_name}"
    messages = redis_client.lrange(queue_key, 0, -1)

    for msg_data in messages:
        try:
            decoded = encoder.decode(msg_data)
            msg = Message.decode(decoded)
            if msg.message_id == task_id:
                redis_client.lrem(queue_key, 0, msg_data)
                update_task_status(task_id, "cancelled")
                return True
        except Exception:
            continue

    update_task_status(task_id, "cancelled")
    return False
