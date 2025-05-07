import asyncio
import random

from backend.utils.parser import parse_text
from backend.utils.extract_helper import extract_text
from backend.utils.s3_uploader import upload_file_to_s3
from backend.cron_jobs.logging_conf import logger

delay = random.uniform(0.1, 0.5)

async def _process_files(file):
    logger.info(f"Started processing file: {file}")
    await asyncio.sleep(0.2)

    unq_id = "generated_unique_id"

    try:
        text, is_image_pdf = await extract_text(file)
        logger.info(f"Extracted text from file: {file}, is_image_pdf={is_image_pdf}")
    except Exception as e:
        logger.error(f"Failed to extract text from file {file}: {e}")
        raise

    if not is_image_pdf:
        try:
            await parse_text(text)
            logger.info(f"Parsed text for file: {file}")
        except Exception as e:
            logger.error(f"Failed to parse text for file {file}: {e}")
            raise

    await asyncio.sleep(delay)  # Simulate delay in upload

    try:
        upload_file_to_s3(file, "some-job", unq_id)
        logger.info(f"Uploaded file to S3: {file} with id: {unq_id}")
    except Exception as e:
        logger.error(f"Failed to upload file {file} to S3: {e}")
        raise

    logger.info(f"Finished processing file: {file}")
