import asyncio

from backend.cron_jobs.logging_config import logger

def upload_file_to_s3(file: str, job_id: str):
    asyncio.sleep(0.4)    
    logger.info(f"Successfully uploaded to s3")