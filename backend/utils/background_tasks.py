import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Retries
# from dramatiq import get_current_message
from asgiref.sync import async_to_sync

from backend.dramatiq_config.dramatiq_config import REDIS_URL
from backend.processors.background import _background_processing
from backend.processors.zip_handler import _process_zip_extracted_files
from backend.cron_jobs.logging_config import logger

from backend.task_tracking.tracker import create_task_record, update_task_status, is_task_cancelled

# Setup Redis Broker with retry middleware
broker = RedisBroker(url="redis://127.0.0.1:6379/0")
broker.add_middleware(Retries(max_retries=3, min_backoff=1000))
dramatiq.set_broker(broker)


@dramatiq.actor(queue_name="zip-file-process")
def background_processing(
    extracted_dir: list, batch_id: str, job_id: str, user_id: str, company_id: str,
    message = None
    ):
    task_id = message.message_id

    if is_task_cancelled(task_id):
        logger.info(f"Task {task_id} was cancelled before start.")
        return

    update_task_status(task_id, "processing")

    try:
        async_to_sync(_background_processing)(extracted_dir, batch_id, job_id, user_id, company_id)
        update_task_status(task_id, "done")
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
        update_task_status(task_id, "failed")
        raise


@dramatiq.actor(queue_name="process_zip_extracted_files", max_retries=3, min_backoff=2000)
def process_zip_extracted_files(
    extracted_dir: str, batch_id: str, job_id: str, user_id: str, company_id: str
):
    task_id = f"{job_id}-zip-handler"

    if is_task_cancelled(task_id):
        logger.info(f"Task {task_id} was cancelled before start.")
        return

    update_task_status(task_id, "processing")

    try:
        async_to_sync(_process_zip_extracted_files)(
            extracted_dir, batch_id, job_id, user_id, company_id
        )
        update_task_status(task_id, "done")
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
        update_task_status(task_id, "failed")
        raise
