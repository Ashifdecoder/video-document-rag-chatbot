from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChunkSchema(BaseModel):
    id: str
    chunk_index: int
    text: str
    start_time: float
    end_time: float

    class Config:
        from_attributes = True

class DocumentCreate(BaseModel):
    title: Optional[str] = None
    file_name: str
    file_type: str

class DocumentUpdate(BaseModel):
    title: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    file_name: str
    file_type: str
    file_size: Optional[int]
    duration: Optional[float]
    status: str
    transcription_status: str
    transcription: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]
    chunks: List[ChunkSchema] = []

    class Config:
        from_attributes = True
