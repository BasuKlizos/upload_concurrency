import os
import asyncio
import dramatiq

from dramatiq.brokers.redis import RedisBroker
from asgiref.sync import async_to_sync

from backend.dramatiq_config.dramatiq_config import REDIS_URL
from backend.processors.background import _background_processing
from backend.processors.zip_handler import _process_zip_extracted_files

broker = RedisBroker(url=REDIS_URL)
dramatiq.set_broker(broker)



broker.declare_queue("zip-file-process")
broker.declare_queue("process_zip_extracted_files")

@dramatiq.actor(queue_name="zip-file-process")
def background_processing(
    extracted_dir: list, batch_id: str, job_id: str, user_id: str, company_id: str
):
    # asyncio.run(_process_zip_extracted_files(extracted_dir, batch_id, job_id, user_id, company_id))
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(
    #     _background_processing(extracted_dir, batch_id, job_id, user_id, company_id)
    # )
    # loop.close()

    async_to_sync(_background_processing)(
        extracted_dir, batch_id, job_id, user_id, company_id
    )


@dramatiq.actor(queue_name="process_zip_extracted_files")
def process_zip_extracted_files(
    extracted_dir: str, batch_id: str, job_id: str, user_id: str, company_id: str
):
    async_to_sync(_process_zip_extracted_files)(
        extracted_dir, batch_id, job_id, user_id, company_id
    )

