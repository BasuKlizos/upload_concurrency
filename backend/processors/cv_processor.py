import asyncio
import random
from backend.utils.compatibility import get_analysis
from backend.cron_jobs.logging_config import logger
from backend.utils.extract_helper import extract_text
from backend.utils.parser import parse_text
from backend.utils.db import db

async def _process_files(file_path: str):
    logger.info(f"Started processing file: {file_path}")

    unq_id = "generated_unique_id"
    
    try:
        text, is_image_pdf = await extract_text(file_path)
        logger.info(f"Extracted text from file: {file_path}, is_image_pdf={is_image_pdf}")
    except Exception as e:
        logger.error(f"Failed to extract text from file {file_path}: {e}")
        raise

    if not is_image_pdf:
        try:
            await parse_text(text)
            logger.info(f"Parsed text for file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to parse text for file {file_path}: {e}")
            raise

    try:
        await upload_file_to_db(file_path, unq_id)
        logger.info(f"Uploaded file to DB: {file_path} with id: {unq_id}")
    except Exception as e:
        logger.error(f"Failed to upload file {file_path} to DB: {e}")
        raise

    logger.info(f"Finished processing file: {file_path}")
    return {"file": file_path, "id": unq_id}

async def upload_file_to_db(file_path: str, unq_id: str):
    file_data = {
        "file_name": file_path,
        "status": "Processing",
        "unique_id": unq_id,
        "content": "Simulated content"  
    }
    
    await db.insert_file(file_data)

# async def extract_text(file_path: str):
#     await asyncio.sleep(0.1)
#     return "Extracted text", False

# async def parse_text(text: str):
#     await asyncio.sleep(0.1)
#     pass

async def upload_file_to_s3(file_path: str, job_id: str):
    await asyncio.sleep(0.2)  
    logger.info(f"Successfully uploaded to s3: {file_path} for job {job_id}")
