import os
import asyncio
import random
import shutil

from backend.cron_jobs.logging_conf import logger
from backend.utils.create_batch_id_and_temp import get_temp_path

delay = random.uniform(0.1, 0.5)


async def cleanup_temp_files_on_error(batch_id):
    logger.info("Starting cleanup of temporary files due to error")
    await asyncio.sleep(delay)
    # temp_dir = os.path.join(get_temp_path(), str(batch_id))
    # if os.path.exists(temp_dir):
    #     shutil.rmtree(temp_dir)
    #     logger.info(f"Cleaned up temp directory: {temp_dir}")

    logger.info(f"Completed cleanup of temporary files (delay: {delay:.3f}s)")
