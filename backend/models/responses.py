"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel
from typing import List, Optional
import base64

class FileInfo(BaseModel):
    """Model for file information."""
    filename: str
    content_type: str
    size: int

class UploadResponse(BaseModel):
    """Model for upload response."""
    message: str
    files: List[FileInfo]

class HealthResponse(BaseModel):
    """Model for health check response."""
    message: str

class AudioMetadata(BaseModel):
    """Model for audio metadata."""
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    year: Optional[int]
    genre: Optional[str]
    cover_art: Optional[str] = None  # Base64 encoded cover art
    cover_art_mime_type: Optional[str] = None  # MIME type of the cover art

class AudioUploadResponse(BaseModel):
    """Model for audio upload response."""
    success: bool
    filename: str
    metadata: AudioMetadata
    message: str

class AudioUpdateRequest(BaseModel):
    """Model for audio metadata update request."""
    metadata: AudioMetadata