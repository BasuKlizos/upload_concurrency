import os
import asyncio
import dramatiq

from asgiref.sync import async_to_sync

from backend.processors.file_chunker import _process_file_chunks
from backend.cron_jobs.logging_conf import logger
async def _process_zip_extracted_files(extracted_dir: str, batch_id: str, job_id: str, user_id: str, company_id: str):
    # print(f"Processing zip file: {extracted_dir}")
    logger.info(f"Processing zip file: {extracted_dir}")
    files = [f for f in os.listdir(extracted_dir) if f.endswith((".pdf", ".docx"))]
    chunks = [files[i : i + 4] for i in range(0, len(files), 4)]
    semaphore = asyncio.Semaphore(8)

    # print("------chuck-------",chunks)
    chunk_tasks = [process_with_semaphore(chunk, semaphore) for chunk in chunks]
    await asyncio.gather(*chunk_tasks)

    # print(f"Finished processing {extracted_dir}")
    logger.info(f"Finished processing {extracted_dir}")

async def process_with_semaphore(chunk: list, semaphore: asyncio.Semaphore):
    async with semaphore:
        # print(f"-------chunk----------",chunk)
        tasks = [asyncio.create_task(_process_file_chunks(file)) for file in chunk]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # print(f"Processed chunk: {results}")
        logger.info(f"Processed chunk: {results}")