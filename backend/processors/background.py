import asyncio

# from backend.utils.background_tasks import process_zip_extracted_files
# from backend.processors.zip_handler import _process_zip_extracted_files
from backend.processors.vectorizer import process_candidates_and_vectorize
from backend.processors.cleanup import cleanup_temp_files_on_error
from backend.corn_jobs.corn_jobs import logger

async def _background_processing(extracted_dirs, batch_id, job_id, user_id, company_id):
    logger.info(f"Starting background processing for batch_id={batch_id}, job_id={job_id}")
    asyncio.sleep(0.5)
    from backend.utils.background_tasks import process_zip_extracted_files
    for extracted_dir in extracted_dirs:
        logger.info(f"Starting processing for extracted directory: {extracted_dir}")
        # await _process_zip_extracted_files(extracted_dir, batch_id, job_id, user_id, company_id)
        process_zip_extracted_files.send(extracted_dir, batch_id, job_id, user_id, company_id)
        logger.info(f"Completed processing for extracted directory: {extracted_dir}")

    logger.info("Starting candidate processing and vectorization")
    await process_candidates_and_vectorize()
    logger.info("Completed candidate processing and vectorization")

    logger.info("Starting cleanup of temporary files")
    await cleanup_temp_files_on_error(batch_id)
    logger.info("Cleanup of temporary files completed")

    logger.info(f"Background processing complete for batch_id={batch_id}, job_id={job_id}")
