import uuid
import os

def create_batch_id() -> str:
    return str(uuid.uuid4())

def get_temp_path() -> str:
    # Get the directory containing utils.py
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Combine with 'temp' to get the absolute path of temp directory
    temp_path = os.path.join(current_directory, "tmp")

    return temp_path 