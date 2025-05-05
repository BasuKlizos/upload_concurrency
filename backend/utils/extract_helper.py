import asyncio
import random

from backend.corn_jobs.corn_jobs import logger

delay = random.uniform(0.1, 0.5)

async def extract_text(file_path):
    if file_path.endswith(".pdf"):
        logger.info(f"Extracting text from PDF: {file_path}")
        await asyncio.sleep(delay)
        return "pdf_text", True

    elif file_path.endswith(".docx"):
        logger.info(f"Extracting text from DOCX: {file_path}")
        await asyncio.sleep(delay)
        return "docx_text", False

    logger.warning(f"Unsupported file type for text extraction: {file_path}")
    return "", False
