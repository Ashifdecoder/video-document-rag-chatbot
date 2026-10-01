from fastapi import UploadFile
import os
import shutil
from pathlib import Path
import logging
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)

async def save_uploaded_file(file: UploadFile, file_content: bytes) -> str:
    """Save uploaded file to storage"""
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"File saved: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"File save failed: {e}")
        raise

def delete_file(file_path: str) -> bool:
    """Delete file from storage"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        return False
