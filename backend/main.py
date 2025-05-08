import asyncio
import os
import zipfile
import io
import shutil

from fastapi import FastAPI, Form, HTTPException, status, File, UploadFile, Depends, Request
from fastapi.responses import JSONResponse
from typing import List

# from backend.dramatiq_config.worker import process_zip_extracted_files
# from backend.utils.background_tasks import process_zip_extracted_files
from backend.utils.background_tasks import background_processing
from backend.utils.create_batch_id_and_temp import create_batch_id, get_temp_path
from backend.cron_jobs.logging_config import logger
from backend.task_tracking.tracker import create_task_record
from backend.utils.task_control import cancel_task
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
    request: Request,
    job_id: str = Form(..., description="ID of the job to upload candidates for"),
    batch_name: str = Form(..., description="Name of the batch"),
    files: List[UploadFile] = File(...),
) -> JSONResponse:
    try:
        # Check if batch_name is already taken (simplified validation here)
        # if batch_name in existing_batches:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Batch name already taken",
        #     )

        # print("checking...")

        client_ip = request.client.host
        logger.info(f"Received upload request from IP: {client_ip} | Job ID: {job_id} | Batch Name: {batch_name}")
        await asyncio.sleep(0.1)

        batch_id = create_batch_id()
        print(f"batch_id---: {batch_id}")
        temp_dir = os.path.join(get_temp_path(), str(batch_id))
        os.makedirs(temp_dir, exist_ok=True)
        logger.info(f"Created temporary directory: {temp_dir}")
        
        processed_files = []
        for file in files:
            logger.info(f"Processing file: {file.filename}")
            if file.content_type not in [
                "application/zip",
                "application/x-zip-compressed",
            ]:
                logger.error(f"Invalid file type for {file.filename}: {file.content_type}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is not supported. Only ZIP files are allowed",
                )
            extracted_dir = os.path.join(temp_dir, file.filename.split(".", 1)[0])
            os.makedirs(extracted_dir, exist_ok=True)
            
            contents = await file.read()
            with zipfile.ZipFile(io.BytesIO(contents)) as zip_file:
                zip_file.extractall(extracted_dir)
            
            processed_files.append(extracted_dir)

        logger.info(f"[ZIP EXTRACTED] Batch ID: {batch_id} | Files Processed: {len(processed_files)}")   
        # print("--------processed_files-----",processed_files)

        response = JSONResponse(
            content={"msg": "Processing of candidates started.", "batch_id": str(batch_id), "status": True},
            status_code=status.HTTP_201_CREATED,
        )

        # Trigger background processing for each extracted directory
        # for extracted_dir in processed_files:
        #     logger.info("Sending background task to Dramatiq")
        #     process_zip_extracted_files.send(extracted_dir, batch_id=batch_id, job_id=job_id, user_id="user_data", company_id="company_id")
        #     # process_zip_extracted_files.send(extracted_dir=extracted_dir)
        # logger.info("Sending background task to Dramatiq")

        logger.info("Sending background task to Dramatiq")
        # background_processing.send(processed_files, batch_id=batch_id, job_id=job_id, user_id="hasbdbh", company_id="hga625")
        
        msg = background_processing.send(
            processed_files, batch_id=batch_id, job_id=job_id, user_id="hasbdbh", company_id="hga625"
        )

        task_id = msg.message_id  

        create_task_record(
            task_id=task_id,
            job_type="zip-file-processing",
            metadata={
                "batch_id": batch_id,
                "job_id": job_id,
                "client_ip": client_ip,
                "file_count": len(processed_files)
            }
        )

        return response
    
    except Exception as e:
        logger.exception(f"Error in upload batch {batch_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing upload: {str(e)}"
        )

    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup temp directory: {cleanup_error}")

@app.post("/cancel-task/{task_id}")
async def cancel_task_api(task_id: str):
    queue = "zip-file-process"
    result = cancel_task(task_id, queue)
    return {
        "task_id": task_id,
        "cancelled": result,
        "message": "Cancelled from queue" if result else "Marked cancelled, maybe already running"
    }