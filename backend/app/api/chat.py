from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import List

from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage, SourceReference
from app.models.database import Document
from app.services.database import get_db_session
from app.services.rag import RAGService
from app.core.constants import ErrorMessages

router = APIRouter()
logger = logging.getLogger(__name__)

rag_service = RAGService()

@router.post("/message")
async def chat_message(request: ChatRequest) -> ChatResponse:
    """Send a message and get a response with sources"""
    try:
        db = next(get_db_session())
        try:
            # Verify document exists
            doc = db.query(Document).filter(Document.id == request.document_id).first()
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ErrorMessages.DOCUMENT_NOT_FOUND
                )
            
            if doc.status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Document processing is not complete. Please wait."
                )
            
            # Get RAG response
            response, sources = await rag_service.query(
                document_id=request.document_id,
                query=request.message,
                chat_history=request.chat_history
            )
            
            # Format source references
            source_refs = [
                SourceReference(
                    chunk_id=source["id"],
                    start_time=source["start_time"],
                    end_time=source["end_time"],
                    text=source["text"],
                    similarity_score=source.get("score")
                )
                for source in sources
            ]
            
            return ChatResponse(
                message=response,
                sources=source_refs,
                timestamp=0
            )
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )

@router.get("/{document_id}/history")
async def get_chat_history(document_id: str):
    """Get chat history for a document"""
    db = next(get_db_session())
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.DOCUMENT_NOT_FOUND
            )
        
        # TODO: Implement chat history retrieval from Redis
        return {"history": []}
    finally:
        db.close()
