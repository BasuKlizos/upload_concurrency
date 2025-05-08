import asyncio
import random

from backend.cron_jobs.logging_config import logger

delay = random.uniform(0.1, 0.5)

async def process_candidates_and_vectorize():
    logger.info("Starting candidate embedding and vectorization")

    async def embed_and_store():
        logger.info(f"Simulating delay before embedding: {delay:.3f}s")
        await asyncio.sleep(delay)
        await _create_embeddings()

    await embed_and_store()
    logger.info("Finished candidate embedding and vectorization")

async def _create_embeddings():
    logger.info(f"Creating embeddings with simulated delay: {delay:.3f}s")
    await asyncio.sleep(delay)
    logger.info("Embeddings created successfully")
