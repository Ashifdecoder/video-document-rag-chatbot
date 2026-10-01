from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
import os
import uuid
from typing import List

from app.core.config import settings
from app.core.constants import VIDEO_EXTENSIONS, AUDIO_EXTENSIONS, ProcessingStatus, ErrorMessages
from app.schemas.document import DocumentResponse, DocumentCreate
from app.models.database import Document
from app.services.database import get_db, get_db_session
from app.services.storage import save_uploaded_file
from app.tasks.process_media import process_media_file

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), title: str = None):
    """Upload and process a video or audio file"""
    try:
        # Validate file
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.INVALID_FILE_TYPE.format(", ".join(settings.ALLOWED_EXTENSIONS))
            )
        
        # Check file size
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.MAX_FILE_SIZE * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=ErrorMessages.FILE_TOO_LARGE.format(settings.MAX_FILE_SIZE)
            )
        
        # Reset file position
        await file.seek(0)
        
        # Save file
        file_path = await save_uploaded_file(file, file_content)
        
        # Create document record
        db = next(get_db_session())
        try:
            file_type = "video" if file_ext in VIDEO_EXTENSIONS else "audio"
            doc = Document(
                title=title or file.filename,
                file_path=file_path,
                file_name=file.filename,
                file_type=file_ext,
                file_size=file_size,
                status=ProcessingStatus.PENDING,
                transcription_status=ProcessingStatus.PENDING
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            
            # Trigger async processing
            process_media_file.delay(doc.id, file_path)
            
            logger.info(f"Document uploaded: {doc.id}")
            return {
                "id": doc.id,
                "message": "File uploaded successfully. Processing started.",
                "status": "processing"
            }
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get document details"""
    db = next(get_db_session())
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.DOCUMENT_NOT_FOUND
            )
        return DocumentResponse.from_orm(doc)
    finally:
        db.close()

@router.get("/{document_id}/status")
async def get_document_status(document_id: str):
    """Get document processing status"""
    db = next(get_db_session())
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.DOCUMENT_NOT_FOUND
            )
        return {
            "id": doc.id,
            "status": doc.status,
            "transcription_status": doc.transcription_status,
            "error_message": doc.error_message,
            "processed_at": doc.processed_at
        }
    finally:
        db.close()

@router.get("")
async def list_documents(skip: int = 0, limit: int = 10):
    """List all documents"""
    db = next(get_db_session())
    try:
        docs = db.query(Document).offset(skip).limit(limit).all()
        total = db.query(Document).count()
        return {
            "total": total,
            "items": [DocumentResponse.from_orm(doc) for doc in docs]
        }
    finally:
        db.close()

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its file"""
    db = next(get_db_session())
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.DOCUMENT_NOT_FOUND
            )
        
        # Delete file
        try:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
        except Exception as e:
            logger.warning(f"Could not delete file {doc.file_path}: {e}")
        
        # Delete from database
        db.delete(doc)
        db.commit()
        
        return {"message": "Document deleted successfully"}
    finally:
        db.close()
