import asyncio
import os
import zipfile
import io
import shutil

from fastapi import FastAPI, Form, HTTPException, status, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from typing import List

# from backend.dramatiq_config.worker import process_zip_extracted_files
# from backend.utils.background_tasks import process_zip_extracted_files
from backend.utils.background_tasks import background_processing
from backend.utils.create_batch_id_and_temp import create_batch_id, get_temp_path
from backend.corn_jobs.corn_jobs import logger
# from app.config import REDIS_URL

app = FastAPI()


@app.get("/")
async def health():
    return JSONResponse(
        content={"status": True, "message": "I am healthy"},
        status_code=status.HTTP_200_OK,
    )


@app.post(
    "/upload",
    summary="Upload candidates via zip file",
    response_description="Return HTTP 201 Created",
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
)
async def upload_candidates(
    job_id: str = Form(..., description="ID of the job to upload candidates for"),
    batch_name: str = Form(..., description="Name of the batch"),
    files: List[UploadFile] = File(...),
) -> JSONResponse:
    # Check if batch_name is already taken (simplified validation here)
    # if batch_name in existing_batches:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Batch name already taken",
    #     )

    print("checking...")
    await asyncio.sleep(0.1)

    batch_id = create_batch_id()
    print(f"batch_id---: {batch_id}")
    temp_dir = os.path.join(get_temp_path(), str(batch_id))
    os.makedirs(temp_dir, exist_ok=True)
    
    processed_files = []
    for file in files:
        extracted_dir = os.path.join(temp_dir, file.filename.split(".", 1)[0])
        os.makedirs(extracted_dir, exist_ok=True)
        
        contents = await file.read()
        with zipfile.ZipFile(io.BytesIO(contents)) as zip_file:
            zip_file.extractall(extracted_dir)
        
        processed_files.append(extracted_dir)
    print("--------processed_files-----",processed_files)

    # Trigger background processing for each extracted directory
    # for extracted_dir in processed_files:
    #     logger.info("Sending background task to Dramatiq")
    #     process_zip_extracted_files.send(extracted_dir, batch_id=batch_id, job_id=job_id, user_id="user_data", company_id="company_id")
    #     # process_zip_extracted_files.send(extracted_dir=extracted_dir)
    logger.info("Sending background task to Dramatiq")

    background_processing.send(processed_files, batch_id=batch_id, job_id=job_id, user_id="hasbdbh", company_id="hga625")
    

    return JSONResponse(
        content={"msg": "Processing of candidates started.", "batch_id": str(batch_id), "status": True},
        status_code=status.HTTP_201_CREATED,
    )
# TODO intregation testing
