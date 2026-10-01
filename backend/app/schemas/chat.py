from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: Optional[float] = None
    source_chunk_id: Optional[str] = None

class ChatRequest(BaseModel):
    document_id: str
    message: str
    chat_history: List[ChatMessage] = []

class SourceReference(BaseModel):
    chunk_id: str
    start_time: float
    end_time: float
    text: str
    similarity_score: Optional[float] = None

class ChatResponse(BaseModel):
    message: str
    sources: List[SourceReference]
    timestamp: float
