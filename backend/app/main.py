from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.api import documents, chat, health

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events"""
    logger.info("Starting Video & Audio RAG Chatbot")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
    yield
    logger.info("Shutting down application")

app = FastAPI(
    title="Video & Audio RAG Chatbot",
    description="A RAG chatbot for video and audio documents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware - Must be first
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Video & Audio RAG Chatbot API", "version": "1.0.0"}

@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(status_code=200, content="OK")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
