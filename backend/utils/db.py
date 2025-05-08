import motor.motor_asyncio
from pymongo import ASCENDING
from bson import ObjectId
import os
import aiofiles
from backend.cron_jobs.logging_config import logger

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.files_collection = self.db["files"]
        self.errors_collection = self.db["errors"]

    async def insert_file(self, file_data: dict):
        result = await self.files_collection.insert_one(file_data)
        logger.info(f"File inserted into DB with ID: {result.inserted_id}")
        return str(result.inserted_id)

    async def insert_error(self, error_data: dict):
        result = await self.errors_collection.insert_one(error_data)
        logger.error(f"Error logged into DB with ID: {result.inserted_id}")
        return str(result.inserted_id)

    async def get_file_by_id(self, file_id: str):
        file = await self.files_collection.find_one({"_id": ObjectId(file_id)})
        return file

    async def get_error_by_id(self, error_id: str):
        error = await self.errors_collection.find_one({"_id": ObjectId(error_id)})
        return error

    async def update_file(self, file_id: str, update_data: dict):
        result = await self.files_collection.update_one(
            {"_id": ObjectId(file_id)}, {"$set": update_data}
        )
        logger.info(f"File with ID {file_id} updated, matched {result.matched_count} documents.")
        return result.matched_count

    async def remove_file(self, file_id: str):
        result = await self.files_collection.delete_one({"_id": ObjectId(file_id)})
        logger.info(f"File with ID {file_id} removed, matched {result.deleted_count} documents.")
        return result.deleted_count

    async def save_file_to_disk(self, file_path: str, file_id: str):
        try:
            async with aiofiles.open(file_path, 'wb') as file:
                await file.write(b"Some content here")  
            return True
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return False

    async def retrieve_file_from_db(self, file_id: str, save_path: str):
        try:
            file = await self.get_file_by_id(file_id)
            if file:
                is_saved = await self.save_file_to_disk(save_path, file_id)
                return is_saved
            return False
        except Exception as e:
            logger.error(f"Error retrieving file {file_id}: {e}")
            return False

db = MongoDB(uri="mongodb://localhost:27017", db_name="file_processing_db")
