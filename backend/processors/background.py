import asyncio

# from backend.utils.background_tasks import process_zip_extracted_files
# from backend.processors.zip_handler import _process_zip_extracted_files
from backend.processors.vectorizer import process_candidates_and_vectorize
from backend.processors.cleanup import cleanup_temp_files_on_error
from backend.cron_jobs.logging_conf import logger

async def _background_processing(extracted_dirs, batch_id, job_id, user_id, company_id):
    logger.info(f"[BG PROCESS START] Batch ID: {batch_id}, Job ID: {job_id}")
    asyncio.sleep(0.5)
    from backend.utils.background_tasks import process_zip_extracted_files
    for extracted_dir in extracted_dirs:
        logger.info(f"[DIR PROCESS] Sending to queue: {extracted_dir}")
        # await _process_zip_extracted_files(extracted_dir, batch_id, job_id, user_id, company_id)
        process_zip_extracted_files.send(extracted_dir, batch_id, job_id, user_id, company_id)
        logger.info(f"Completed processing for extracted directory: {extracted_dir}")

    logger.info(f"[VECTORIZATION] Starting candidate processing and vectorization")
    await process_candidates_and_vectorize()
    logger.info(f"[VECTORIZATION] Completed")

    logger.info(f"[CLEANUP] Starting cleanup for Batch ID: {batch_id}")
    await cleanup_temp_files_on_error(batch_id)
    logger.info(f"[CLEANUP] Completed")

    logger.info(f"[BG PROCESS COMPLETE] Batch ID: {batch_id}, Job ID: {job_id}")
