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
from backend.cron_jobs.logging_conf import logger
# from app.config import REDIS_URL

app = FastAPI()


@app.get("/")
async def health():
    return JSONResponse(
        content={"status": True, "message": "I am healthy"},
        status_code=status.HTTP_200_OK,
    )


# @app.post(
#     "/upload",
#     summary="Upload candidates via zip file",
#     response_description="Return HTTP 201 Created",
#     status_code=status.HTTP_201_CREATED,
#     response_class=JSONResponse,
# )
# async def upload_candidates(
#     request: Request,
#     job_id: str = Form(..., description="ID of the job to upload candidates for"),
#     batch_name: str = Form(..., description="Name of the batch"),
#     files: List[UploadFile] = File(...),
# ) -> JSONResponse:
#     # Check if batch_name is already taken (simplified validation here)
#     # if batch_name in existing_batches:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_400_BAD_REQUEST,
#     #         detail="Batch name already taken",
#     #     )

#     client_ip = request.client.host
#     logger.info(f"Received upload request from IP: {client_ip} | Job ID: {job_id} | Batch Name: {batch_name}")

#     await asyncio.sleep(0.1)

#     batch_id = create_batch_id()
#     print(f"batch_id---: {batch_id}")
#     temp_dir = os.path.join(get_temp_path(), str(batch_id))
#     os.makedirs(temp_dir, exist_ok=True)
#     logger.info(f"Created temporary directory: {temp_dir}")
    
#     processed_files = []
#     for file in files:
#         extracted_dir = os.path.join(temp_dir, file.filename.split(".", 1)[0])
#         os.makedirs(extracted_dir, exist_ok=True)
        
#         contents = await file.read()
#         with zipfile.ZipFile(io.BytesIO(contents)) as zip_file:
#             zip_file.extractall(extracted_dir)
        
#         processed_files.append(extracted_dir)
    
#     logger.info(f"[ZIP EXTRACTED] Batch ID: {batch_id} | Files Processed: {len(processed_files)}")
#     # print("--------processed_files-----",processed_files)

#     # Trigger background processing for each extracted directory
#     # for extracted_dir in processed_files:
#     #     logger.info("Sending background task to Dramatiq")
#     #     process_zip_extracted_files.send(extracted_dir, batch_id=batch_id, job_id=job_id, user_id="user_data", company_id="company_id")
#     #     # process_zip_extracted_files.send(extracted_dir=extracted_dir)
#     # logger.info("Sending background task to Dramatiq")
    
#     response = JSONResponse(
#         content={"msg": "Processing of candidates started.", "batch_id": str(batch_id), "status": True},
#         status_code=status.HTTP_201_CREATED,
#     )

#     background_processing.send(processed_files, batch_id=batch_id, job_id=job_id, user_id="hasbdbh", company_id="hga625")
#     logger.info(f"[TASK DISPATCHED] Batch ID: {batch_id} sent for background processing")
    
#     return response
# # TODO intregation testing


jobs = collection("jobs")
batches = collection("batches")


@router.post(
    "/bulk",
    summary="Upload multiple candidate files",
    response_description="Return HTTP 201 Created",
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
)
async def upload_candidates(
    request: Request,
    job_id: str = Form(..., description="ID of the job to upload candidates for"),
    batch_name: str = Form(..., description="Name of the batch"),
    files: List[UploadFile] = File(..., description="Multiple candidate files (PDF, DOCX or ZIP)"),
    send_invitations: bool = Form(False, description="Send interview invitations to qualified candidates"),
    # user_data: UserData = Depends(PermissionChecker([Permission.MANAGE_CANDIDATES])),
) -> JSONResponse:
    if await batches.find_one({"batch_name": batch_name}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch name already taken",
        )

    # Get job data
    job = await get_job_data(job_id)

    # Parse Role and User Details form UserData
    details, _ = user_data

    batch_id = create_batch_id()
    logger.info(f"Starting new upload batch: {batch_id}")

    batch_directory = os.path.join(get_temp_path(), str(batch_id))
    logger.info(f"Temp directory: {batch_directory}")

    try:
        os.makedirs(batch_directory, exist_ok=True)
        for file in files:
            logger.info(f"Processing file: {file.filename}")
            if file.content_type not in [
                "application/zip",
                "application/x-zip-compressed",
                "application/pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ]:
                logger.error(f"Invalid file type for {file.filename}: {file.content_type}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is not supported. Only ZIP files are allowed",
                )

            # Check file type and process accordingly
            if file.content_type in ["application/zip", "application/x-zip-compressed"]:
                contents = await file.read()
                with zipfile.ZipFile(io.BytesIO(contents)) as zip_file:
                    zip_file.extractall(batch_directory)
            elif file.content_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                file_path = os.path.join(batch_directory, file.filename)
                with open(file_path, "wb") as f:
                    f.write(await file.read())
            else:
                logger.error(f"Invalid file type for {file.filename}: {file.content_type}, Skipping file")
                continue

        # Get the count of files in the batch directory
        file_count = len(os.listdir(batch_directory))

        # Insert batch record and update job count before background processing
        await batches.insert_one(
            {
                "uploaded_by": ObjectId(details.get("user_id")),
                "company_id": ObjectId(job.get("company_id")),
                "batch_id": Binary.from_uuid(batch_id),
                "batch_name": batch_name,
                "upload_count": file_count,
                "job_id": ObjectId(job_id),
                "status": "processing",
                "start_time": get_current_time_utc(),
            }
        )

        await jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"updated_at": get_current_time_utc()}, "$inc": {"selection_progress.total_candidate_count": file_count}},
        )

        # Create response before background processing
        response = JSONResponse(
            content={
                "msg": f"Processing of {file_count} candidates started. You will receive an email when complete",
                "batch_id": str(batch_id),
                "status": True,
            },
            status_code=status.HTTP_201_CREATED,
        )

        # Process all extracted directories in background
        async def background_processing():
            try:
                if os.path.exists(batch_directory):
                    logger.info(f"Starting background processing for directory: {batch_directory}")
                    await process_zip_extracted_files(
                        extracted_dir=batch_directory,
                        batch_id=batch_id,
                        job_id=job_id,
                        user_id=details.get("user_id"),
                        company_id=details.get("company_id"),
                        send_invitations=send_invitations,
                    )

                    # Send Processing completion email to user
                    await send_processing_completion_email(batch_id, details, job.get("title"), request)
                else:
                    logger.error(f"Extracted directory does not exist: {batch_directory}")

            except Exception as e:
                logger.exception(f"Error in upload batch {batch_id}: {str(e)}")
                try:
                    shutil.rmtree(batch_directory)
                    logger.debug(f"Cleaned up temp directory after error: {batch_directory}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup temp directory: {cleanup_error}", exc_info=True)

        asyncio.create_task(background_processing())
        return response

    except Exception as e:
        logger.exception(f"Error in upload batch {batch_id}: {str(e)}")
        # Cleanup on error
        try:
            shutil.rmtree(batch_directory)
            logger.debug(f"Cleaned up temp directory after error: {batch_directory}")
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup temp directory: {cleanup_error}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing upload: {str(e)}",
        )