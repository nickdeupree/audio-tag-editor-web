"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel
from typing import List, Optional

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
    platform: Optional[str] = None  # Platform where the audio was sourced from (youtube, soundcloud, upload)
    original_url: Optional[str] = None  # Original URL for downloaded content
    all_files_metadata: Optional[List[dict]] = None  # Metadata for all uploaded files

class AudioUpdateRequest(BaseModel):
    """Model for audio metadata update request."""
    metadata: AudioMetadata