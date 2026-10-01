import logging
from typing import List
import json

from app.tasks.celery_app import celery_app
from app.core.config import settings
from app.core.constants import ProcessingStatus
from app.models.database import Document, Chunk
from app.services.database import SessionLocal
from app.services.transcription import transcription_service
from app.services.embedding import embedding_service
import chromadb

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="process_media_file")
def process_media_file(self, document_id: str, file_path: str):
    """Process media file: transcribe and create embeddings"""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document not found: {document_id}")
        
        # Update status
        doc.status = ProcessingStatus.PROCESSING
        doc.transcription_status = ProcessingStatus.PROCESSING
        db.commit()
        
        logger.info(f"Starting processing for document: {document_id}")
        
        # Transcribe
        logger.info(f"Transcribing file: {file_path}")
        transcription_result = transcription_service.transcribe(file_path)
        
        # Extract text and segments
        full_text = transcription_result.get("text", "")
        segments = transcription_result.get("segments", [])
        
        doc.transcription = full_text
        doc.transcription_status = ProcessingStatus.COMPLETED
        db.commit()
        
        logger.info(f"Transcription completed for document: {document_id}")
        
        # Create chunks
        chunks = create_chunks(segments, document_id)
        
        # Create Chroma collection and add embeddings
        chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_URL.split("://")[1].split(":")[0],
            port=int(settings.CHROMA_URL.split(":")[-1])
        )
        
        collection_name = f"doc_{document_id}"
        try:
            collection = chroma_client.get_collection(name=collection_name)
        except:
            collection = chroma_client.create_collection(name=collection_name)
        
        # Add chunks to database and Chroma
        logger.info(f"Creating embeddings for {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            # Add to database
            db_chunk = Chunk(
                document_id=document_id,
                chunk_index=i,
                text=chunk["text"],
                start_time=chunk["start_time"],
                end_time=chunk["end_time"]
            )
            db.add(db_chunk)
            db.flush()
            
            # Add to Chroma
            collection.add(
                ids=[db_chunk.id],
                documents=[chunk["text"]],
                metadatas=[{
                    "document_id": document_id,
                    "chunk_index": i,
                    "start_time": chunk["start_time"],
                    "end_time": chunk["end_time"]
                }]
            )
            
            db_chunk.embedding_id = db_chunk.id
        
        db.commit()
        
        # Update document status
        doc.status = ProcessingStatus.COMPLETED
        db.commit()
        
        logger.info(f"Processing completed for document: {document_id}")
        return {"status": "completed", "document_id": document_id, "chunks": len(chunks)}
        
    except Exception as e:
        logger.error(f"Processing failed for document {document_id}: {e}")
        doc.status = ProcessingStatus.FAILED
        doc.error_message = str(e)
        db.commit()
        raise
    finally:
        db.close()

def create_chunks(segments: List[dict], document_id: str) -> List[dict]:
    """Create chunks from transcription segments"""
    chunks = []
    current_chunk = {
        "text": "",
        "start_time": 0,
        "end_time": 0,
        "token_count": 0
    }
    
    for segment in segments:
        text = segment.get("text", "").strip()
        if not text:
            continue
        
        token_count = len(text.split())
        
        # Check if adding this segment exceeds chunk size
        if current_chunk["token_count"] + token_count > settings.CHUNK_SIZE:
            if current_chunk["text"]:
                chunks.append({
                    "text": current_chunk["text"],
                    "start_time": current_chunk["start_time"],
                    "end_time": current_chunk["end_time"]
                })
            current_chunk = {
                "text": text,
                "start_time": segment.get("start", 0),
                "end_time": segment.get("end", 0),
                "token_count": token_count
            }
        else:
            if not current_chunk["text"]:
                current_chunk["start_time"] = segment.get("start", 0)
            current_chunk["text"] += " " + text
            current_chunk["end_time"] = segment.get("end", 0)
            current_chunk["token_count"] += token_count
    
    # Add final chunk
    if current_chunk["text"]:
        chunks.append({
            "text": current_chunk["text"],
            "start_time": current_chunk["start_time"],
            "end_time": current_chunk["end_time"]
        })
    
    return chunks
