import asyncio
import httpx
import uuid
import traceback

error_count, success_count= 0, 0
timeout = httpx.Timeout(60.0)

# async def upload_zip():
#     try:
#         url = "http://localhost:8000/upload"

#         # Form data
#         form_data = {
#             "job_id": "1235",
#             "batch_name": "python developer 2023",
#         }

#         # zip_path = r"C:\Users\Sourabh Kumar Das\Downloads\sample-local-pdf (2).zip"
#         # zip_path = "C:\\Users\\Sourabh Kumar Das\\Downloads\\sample-local-pdf (2).zip"
#         # zip_path = r"C:\Users\Sourabh Kumar Das\Downloads\sample-report_new.zip"
#         zip_path = r"C:\Users\Basudev Samanta\Downloads\sample-report_new.zip"

#         # Prepare the file to send as multipart
#         with open(zip_path, "rb") as f:
#             files = {"files": (f"{uuid.uuid4().hex[:5]}file.zip", f, "application/zip")}

#             async with httpx.AsyncClient() as client:
#                 response = await client.post(url, data=form_data, files=files)

#         print(f"Status code: {response.status_code}")
#         print("Response body:", response.text)
#         if response.status_code == 201:
#             global sucess_count
#             sucess_count +=1
#         # else:
#         #     global error_count
#         #     error_count +=1

#     except Exception as e:
#         print(f"Unexpected error occured: {e}")
#         global error_count
#         error_count +=1

async def upload_zip():
    global error_count, success_count
    try:
        url = "http://localhost:8000/upload"

        # Form data
        form_data = {
            "job_id": "1235",
            "batch_name": "python developer 2023",
        }

        # Path to your ZIP file
        zip_path = r"C:\Users\Basudev Samanta\Downloads\sample-report_new.zip"

        # Prepare the file to send as multipart
        # with open(zip_path, "rb") as f:
        #     files = {"files": (f"{uuid.uuid4().hex[:5]}file.zip", f, "application/zip")}

        #     async with httpx.AsyncClient() as client:
        #         response = await client.post(url, data=form_data, files=files)

        with open(zip_path, "rb") as f:
            filename = f"{uuid.uuid4().hex[:5]}_candidates.zip"
            
            # `files` must be a list of tuples, because FastAPI expects a List[UploadFile]
            files = [
                ("files", (filename, f, "application/zip"))
            ]

            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=form_data, files=files)


        print(f"Status code: {response.status_code}")
        # print("Response body:", response.text)

        if response.status_code == 201:
            success_count += 1
        else:
            print(f"Upload failed with status code: {response.status_code}")
            error_count += 1

    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        traceback.print_exc()
        error_count += 1

async def upload_multiple(n: int):
    tasks = [upload_zip() for _ in range(n)]
    await asyncio.gather(*tasks)


async def upload_multiple_with_bg_task(n: int):
    print(n)
    # tasks = [asyncio.create_task(upload_zip()) for _ in range(n)]
    # await asyncio.gather(*tasks)

    tasks = []

    for i in range(n):
        print(f"Starting task {i}")
        # await asyncio.sleep(1)
        # asyncio.create_task(upload_zip())
        tasks.append(
            asyncio.create_task(upload_zip())
        )

    await asyncio.gather(*tasks)
    # print("done- > ")




    await asyncio.sleep(10)


if __name__ == "__main__":
    # asyncio.run(upload_zip())
    # asyncio.run(upload_multiple(30))

    asyncio.run(upload_multiple_with_bg_task(10))
    print(f"Success_count: {success_count}")
    print(f"Error_count: {error_count}")