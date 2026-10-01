import whisper
import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            self.model = whisper.load_model(settings.WHISPER_MODEL)
            logger.info(f"Whisper model loaded: {settings.WHISPER_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(self, file_path: str) -> dict:
        """Transcribe audio/video file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            logger.info(f"Starting transcription: {file_path}")
            result = self.model.transcribe(file_path, language="en")
            
            logger.info(f"Transcription completed for: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

transcription_service = TranscriptionService()
