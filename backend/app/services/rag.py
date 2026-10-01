import chromadb
from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
import logging
from typing import Tuple, List

from app.core.config import settings
from app.models.database import Document, Chunk
from app.services.database import SessionLocal

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_URL.split("://")[1].split(":")[0],
            port=int(settings.CHROMA_URL.split(":")[-1])
        )
        self.llm = ChatOpenAI(
            model_name=settings.OPENAI_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    async def query(self, document_id: str, query: str, chat_history: list = None) -> Tuple[str, List[dict]]:
        """Query document with RAG"""
        try:
            db = SessionLocal()
            try:
                # Get document
                doc = db.query(Document).filter(Document.id == document_id).first()
                if not doc:
                    raise ValueError(f"Document not found: {document_id}")
                
                # Get collection from Chroma
                collection = self.chroma_client.get_collection(
                    name=f"doc_{document_id}"
                )
                
                # Search for similar chunks
                results = collection.query(
                    query_texts=[query],
                    n_results=settings.TOP_K
                )
                
                # Format sources
                sources = []
                chunks_text = ""
                
                if results and results["documents"]:
                    for i, doc_text in enumerate(results["documents"][0]):
                        chunks_text += doc_text + "\n\n"
                        
                        chunk_id = results["ids"][0][i]
                        score = results["distances"][0][i] if "distances" in results else None
                        
                        # Get chunk details
                        chunk = db.query(Chunk).filter(Chunk.embedding_id == chunk_id).first()
                        sources.append({
                            "id": chunk_id,
                            "start_time": chunk.start_time if chunk else 0,
                            "end_time": chunk.end_time if chunk else 0,
                            "text": doc_text,
                            "score": score
                        })
                
                # Build prompt
                prompt = f"""Based on the following document excerpts, answer the user's question.
                
Document excerpts:
{chunks_text}

User question: {query}

Provide a clear and concise answer based on the document content."""
                
                # Get LLM response
                messages = [
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm(messages)
                answer = response.content
                
                logger.info(f"RAG query successful for document: {document_id}")
                return answer, sources
            finally:
                db.close()
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            raise
