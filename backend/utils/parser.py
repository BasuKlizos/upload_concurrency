from backend.utils.db import db
from backend.cron_jobs.logging_config import logger

async def parse_text(text: str, file_path: str):
    lines = text.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    word_count = sum(len(line.split()) for line in non_empty_lines)
    char_count = sum(len(line) for line in non_empty_lines)

    update_data = {
        "parsed_line_count": len(non_empty_lines),
        "parsed_word_count": word_count,
        "parsed_char_count": char_count,
        "status": "parsed"
    }

    await db.update_file(file_path, update_data)
    logger.info(f"Updated file {file_path} with parsed text stats")