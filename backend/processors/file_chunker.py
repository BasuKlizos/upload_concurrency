import asyncio
import random
from backend.processors.cv_processor import _process_files
from backend.utils.compatibility import get_analysis
from backend.cron_jobs.logging_conf import logger
# from utils.db import candidates, candidates_errors

def valid_results(result):
    return True

async def _process_file_chunks(chunk):
    logger.info(f"Starting processing of chunk: {chunk}")

    tasks = [_process_files(chunk)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid = []
    invalid = []

    for i, result in enumerate(results):
        file_name = chunk[i] if i < len(chunk) else "Unknown"
        if isinstance(result, Exception):
            logger.error(f"Error processing file '{file_name}': {result}")
            await asyncio.sleep(1)
            invalid.append(result)
            continue
        if valid_results(result):
            logger.info(f"Valid result for file '{file_name}': {result}")
            await get_analysis(result)
            valid.append(result)
        else:
            logger.info(f"Invalid result for file '{file_name}': {result}")
            invalid.append(result)

    if valid:
        delay = random.uniform(0.1, 0.5)
        logger.info(f"Sleeping for {delay}ms before bulk write of valid results")
        await asyncio.sleep(delay)
        # await candidates.bulk_write(valid)
        logger.info(f"Processed and wrote {len(valid)} valid results")

    if invalid:
        logger.info(f"Sleeping briefly before handling {len(invalid)} invalid results")
        await asyncio.sleep(0.1)
        # await candidates_errors.insert_many(invalid)
        logger.info(f"Handled {len(invalid)} invalid results")

    logger.info(f"Finished processing chunk: {chunk}")
