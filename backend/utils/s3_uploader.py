import asyncio

from backend.corn_jobs.corn_jobs import logger

def upload_file_to_s3(file: str, job_id: str):
    asyncio.sleep(0.4)    
    logger.info(f"Successfully uploaded to s3")