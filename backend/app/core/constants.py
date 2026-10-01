# File type constants
VIDEO_EXTENSIONS = {"mp4", "webm", "avi", "mov"}
AUDIO_EXTENSIONS = {"mp3", "wav", "m4a", "ogg"}

# Processing status
class ProcessingStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Error messages
class ErrorMessages:
    INVALID_FILE_TYPE = "Invalid file type. Allowed types: {}"
    FILE_TOO_LARGE = "File size exceeds maximum limit of {} MB"
    DOCUMENT_NOT_FOUND = "Document not found"
    PROCESSING_FAILED = "Document processing failed: {}"
    INVALID_REQUEST = "Invalid request"
