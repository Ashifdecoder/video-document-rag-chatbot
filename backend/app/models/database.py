from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Enum, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Document(Base):
    """Video/Audio document model"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # mp4, mp3, etc
    file_size = Column(Integer)  # in bytes
    duration = Column(Float)  # in seconds
    
    # Transcription
    transcription = Column(Text, nullable=True)
    transcription_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    # Metadata
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_document_status", "status"),
        Index("idx_document_created_at", "created_at"),
    )

class Chunk(Base):
    """Document chunk with embeddings"""
    __tablename__ = "chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    
    # Temporal information
    start_time = Column(Float)  # in seconds
    end_time = Column(Float)  # in seconds
    
    # Embedding info
    embedding_id = Column(String(255), nullable=True)  # Chroma collection ID
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    __table_args__ = (
        Index("idx_chunk_document_id", "document_id"),
    )
