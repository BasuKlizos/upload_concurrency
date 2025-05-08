import os
import asyncio
import shutil
import stat
from backend.processors.file_chunker import _process_file_chunks
from backend.cron_jobs.logging_config import logger
from backend.processors.vectorizer import process_candidates_and_vectorize

async def _process_zip_extracted_files(extracted_dir: str, batch_id: str, job_id: str, user_id: str, company_id: str):
    logger.info(f"Processing zip file: {extracted_dir}")
    try:
        files = [os.path.join(extracted_dir, f) for f in os.listdir(extracted_dir) if f.endswith((".pdf", ".docx", ".doc"))]
        chunks = [files[i:i + 4] for i in range(0, len(files), 4)]
        semaphore = asyncio.Semaphore(8)

        chunk_tasks = [process_with_semaphore(chunk, semaphore) for chunk in chunks]
        await asyncio.gather(*chunk_tasks)

        logger.info(f"Finished processing {extracted_dir}")
        logger.info(f"[VECTORIZATION] Starting candidate processing and vectorization")
        await process_candidates_and_vectorize(extracted_dir, batch_id, job_id, company_id, user_id)
        logger.info(f"[VECTORIZATION] Completed")
    
    finally:
        try:
            logger.info(f"Attempting cleanup. Files in {extracted_dir}: {os.listdir(extracted_dir)}")
            def handle_remove_readonly(func, path, exc_info):
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(os.path.dirname(extracted_dir), onerror=handle_remove_readonly)
            logger.info(f"Successfully cleaned up directory: {extracted_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup directory {extracted_dir}: {e}", exc_info=True)

async def process_with_semaphore(chunk: list, semaphore: asyncio.Semaphore):
    async with semaphore:
        await _process_file_chunks(chunk)
