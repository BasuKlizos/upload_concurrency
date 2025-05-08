import os
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from docx import Document
from backend.cron_jobs.logging_config import logger
from backend.utils.db import db  # <-- import your db instance

async def extract_text(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    is_image_pdf = False
    extracted_text = ""

    try:
        if ext == ".pdf":
            logger.info(f"Extracting text from PDF: {file_path}")
            extracted_text, is_image_pdf = await extract_from_pdf(file_path)
        elif ext == ".docx":
            logger.info(f"Extracting text from DOCX: {file_path}")
            extracted_text = extract_from_docx(file_path)
        elif ext == ".doc":
            logger.warning(f".doc format not supported. Please convert to .docx: {file_path}")
            extracted_text = "Unsupported format: .doc"
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        raise

    text_doc = {
        "file_name": os.path.basename(file_path),
        "file_path": file_path,
        "file_type": ext,
        "extracted_text": extracted_text,
        "is_image_pdf": is_image_pdf,
        "status": "extracted"
    }
    await db.insert_file(text_doc)

    return extracted_text, is_image_pdf

async def extract_from_pdf(file_path: str):
    text = ""
    is_image_pdf = False
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        logger.error(f"PyPDF2 failed for {file_path}: {e}")
        text = ""

    if not text.strip():
        try:
            images = convert_from_path(file_path)
            is_image_pdf = True
            for image in images:
                text += pytesseract.image_to_string(image)
        except Exception as e:
            logger.error(f"OCR failed for {file_path}: {e}")
            raise

    return text.strip(), is_image_pdf

def extract_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs).strip()