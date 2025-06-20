"""
Service for handling audio tag updates and cover art operations.
"""

import json
import tempfile
import os
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from services.audio_service import AudioService
from models.responses import AudioMetadata


class TagUpdateService:
    """Service for handling audio tag updates and cover art operations."""
    
    def __init__(self):
        """Initialize the tag update service."""
        self.audio_service = AudioService()
    
    def parse_metadata_from_form(self, metadata_str: str) -> AudioMetadata:
        """Parse metadata from form data string."""
        try:
            metadata_dict = json.loads(metadata_str)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid metadata JSON: {str(e)}")
        
        if not isinstance(metadata_dict, dict):
            raise HTTPException(status_code=400, detail="Metadata must be a JSON object")
        
        # Create AudioMetadata object with proper null handling
        return AudioMetadata(
            title=metadata_dict.get('title') if metadata_dict.get('title') else None,
            artist=metadata_dict.get('artist') if metadata_dict.get('artist') else None,
            album=metadata_dict.get('album') if metadata_dict.get('album') else None,
            genre=metadata_dict.get('genre') if metadata_dict.get('genre') else None,
            year=metadata_dict.get('year') if metadata_dict.get('year') else None,
            cover_art=metadata_dict.get('cover_art') if metadata_dict.get('cover_art') else None,
            cover_art_mime_type=metadata_dict.get('cover_art_mime_type') if metadata_dict.get('cover_art_mime_type') else None
        )
    
    async def update_file_tags(self, file: UploadFile, metadata_str: str) -> Dict[str, Any]:
        """Update audio file tags with new metadata."""
        if not file.filename.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Parse metadata
        metadata = self.parse_metadata_from_form(metadata_str)
        
        temp_file_path = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Update metadata
            success = self.audio_service.update_metadata(temp_file_path, metadata)
            
            if success:
                # Return the updated file content
                with open(temp_file_path, 'rb') as updated_file:
                    updated_content = updated_file.read()
                
                return {
                    "success": True,
                    "message": "Tags updated successfully",
                    "filename": file.filename,
                    "updated_content": updated_content
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to update tags")
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating file: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
    
    async def update_cover_art(self, audio_file: UploadFile, cover_file: UploadFile) -> Dict[str, Any]:
        """Update cover art for an audio file."""
        # Validate audio file type
        audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
        if not audio_file.filename.lower().endswith(audio_extensions):
            raise HTTPException(status_code=400, detail="Unsupported audio file format")
        
        # Validate cover art file type
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        if not cover_file.filename.lower().endswith(image_extensions):
            raise HTTPException(status_code=400, detail="Unsupported image file format")
        
        audio_temp_path = None
        try:
            # Save audio file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as temp_file:
                audio_content = await audio_file.read()
                temp_file.write(audio_content)
                audio_temp_path = temp_file.name
            
            # Read cover art data
            cover_content = await cover_file.read()
            
            # Detect MIME type
            mime_type = cover_file.content_type or 'image/jpeg'
            if not mime_type.startswith('image/'):
                # Fallback MIME type detection
                if cover_file.filename.lower().endswith('.png'):
                    mime_type = 'image/png'
                elif cover_file.filename.lower().endswith(('.jpg', '.jpeg')):
                    mime_type = 'image/jpeg'
                elif cover_file.filename.lower().endswith('.gif'):
                    mime_type = 'image/gif'
                elif cover_file.filename.lower().endswith('.webp'):
                    mime_type = 'image/webp'
                else:
                    mime_type = 'image/jpeg'
            
            # Encode to base64
            import base64
            cover_b64 = base64.b64encode(cover_content).decode('utf-8')
            
            # Update cover art
            success = self.audio_service.update_cover_art(audio_temp_path, cover_b64, mime_type)
            
            if success:
                return {
                    "success": True,
                    "message": "Cover art updated successfully",
                    "filename": audio_file.filename
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to update cover art")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating cover art: {str(e)}")
        finally:
            # Clean up temporary file
            if audio_temp_path and os.path.exists(audio_temp_path):
                try:
                    os.unlink(audio_temp_path)
                except OSError:
                    pass
