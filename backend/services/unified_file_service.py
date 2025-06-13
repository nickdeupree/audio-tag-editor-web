"""
Unified file service for managing all audio files (uploaded, downloaded, and edited).
"""

import os
import time
import shutil
import zipfile
import tempfile
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from app.services.audio_service import AudioService
from app.services.download_service import DownloadService
from models.responses import AudioMetadata, AudioUploadResponse


class UnifiedFileService:
    """Service for managing all audio files in a unified workspace."""
    
    # Directory constants
    WORKSPACE_DIR = "/tmp/audio_workspace"
    AUDIO_EXTENSIONS = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
    
    def __init__(self):
        """Initialize the unified file service."""
        self.audio_service = AudioService()
        self.download_service = DownloadService()
        self._ensure_workspace_directory()
    
    def _ensure_workspace_directory(self):
        """Ensure the workspace directory exists."""
        os.makedirs(self.WORKSPACE_DIR, exist_ok=True)
    
    def _generate_unique_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate a unique filename with timestamp."""
        timestamp = int(time.time())
        base_name = os.path.splitext(original_filename)[0]
        extension = os.path.splitext(original_filename)[1]
        
        # Clean filename for filesystem compatibility
        clean_name = self._clean_filename(base_name)
        
        if prefix:
            return f"{prefix}_{timestamp}_{clean_name}{extension}"
        else:
            return f"{timestamp}_{clean_name}{extension}"
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename for filesystem compatibility."""
        # Remove or replace problematic characters
        problematic_chars = ['/', '\\', ':', '?', '*', '<', '>', '|', '"']
        for char in problematic_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        return filename[:50]
    
    def _extract_original_filename(self, stored_filename: str) -> str:
        """Extract original filename from stored filename."""
        if "_" in stored_filename and any(stored_filename.startswith(prefix) for prefix in ["upload_", "youtube_", "soundcloud_", "updated_"]):
            # Format: prefix_timestamp_originalname.ext
            parts = stored_filename.split("_", 2)
            return parts[2] if len(parts) > 2 else stored_filename
        return stored_filename
    
    async def add_uploaded_files(self, files: List[UploadFile]) -> AudioUploadResponse:
        """Add uploaded files to the workspace."""
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        all_metadata = []
        stored_files = []
        
        for file in files:
            # Validate file type
            if not file.filename.lower().endswith(self.AUDIO_EXTENSIONS):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format for {file.filename}. Allowed formats: {', '.join(self.AUDIO_EXTENSIONS)}"
                )
            
            temp_file_path = None
            try:
                # Create temporary file for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                
                # Extract metadata
                metadata = self.audio_service.extract_metadata(temp_file_path)
                
                # Generate unique filename for workspace
                unique_filename = self._generate_unique_filename(file.filename, "upload")
                workspace_file_path = os.path.join(self.WORKSPACE_DIR, unique_filename)
                
                # Copy to workspace
                shutil.copy2(temp_file_path, workspace_file_path)
                
                all_metadata.append({
                    'filename': file.filename,
                    'stored_filename': unique_filename,
                    'metadata': metadata
                })
                
                stored_files.append({
                    'original_filename': file.filename,
                    'stored_filename': unique_filename,
                    'file_path': workspace_file_path
                })
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")
            finally:
                # Clean up temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except OSError:
                        pass
        
        # Return response compatible with existing API
        first_file = files[0]
        first_metadata = all_metadata[0]['metadata'] if all_metadata else None
        
        return AudioUploadResponse(
            success=True,
            filename=first_file.filename,
            metadata=first_metadata,
            message=f"{len(files)} file(s) uploaded and added to workspace successfully",
            platform="upload",
            all_files_metadata=all_metadata
        )
    
    async def add_youtube_audio(self, url: str) -> AudioUploadResponse:
        """Download and add YouTube audio to workspace."""
        downloaded_file_path = None
        
        try:
            # Download the audio
            download_result = self.download_service.download_audio(url, output_format='mp3')
            downloaded_file_path = download_result['file_path']
            
            # Extract and enhance metadata
            metadata = self.audio_service.extract_metadata(downloaded_file_path)
            download_metadata = download_result['metadata']
            
            # Enhance metadata with download info
            if not metadata.title and download_metadata.get('title'):
                metadata.title = download_metadata['title']
            if not metadata.artist and download_metadata.get('artist'):
                metadata.artist = download_metadata['artist']
            if not metadata.album and download_metadata.get('album'):
                metadata.album = download_metadata['album']
            if not metadata.year and download_metadata.get('year'):
                metadata.year = download_metadata['year']
            if not metadata.genre and download_metadata.get('genre'):
                metadata.genre = download_metadata['genre']
            
            # Generate unique filename for workspace
            original_title_clean = self._clean_filename(download_result['original_title'])
            unique_filename = self._generate_unique_filename(f"{original_title_clean}.mp3", "youtube")
            workspace_file_path = os.path.join(self.WORKSPACE_DIR, unique_filename)
            
            # Copy to workspace
            shutil.copy2(downloaded_file_path, workspace_file_path)
            
            return AudioUploadResponse(
                success=True,
                filename=unique_filename,
                metadata=metadata,
                message="YouTube audio downloaded and added to workspace successfully",
                platform="youtube",
                original_url=url
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading YouTube audio: {str(e)}")
        finally:
            # Clean up temporary download
            if downloaded_file_path and os.path.exists(downloaded_file_path):
                try:
                    self.download_service.cleanup_download(downloaded_file_path)
                except Exception:
                    pass
    
    async def add_soundcloud_audio(self, url: str) -> AudioUploadResponse:
        """Download and add SoundCloud audio to workspace."""
        downloaded_file_path = None
        
        try:
            # Download the audio
            download_result = self.download_service.download_audio(url, output_format='mp3')
            downloaded_file_path = download_result['file_path']
            
            # Extract and enhance metadata
            metadata = self.audio_service.extract_metadata(downloaded_file_path)
            download_metadata = download_result['metadata']
            
            # Enhance metadata with download info
            if not metadata.title and download_metadata.get('title'):
                metadata.title = download_metadata['title']
            if not metadata.artist and download_metadata.get('artist'):
                metadata.artist = download_metadata['artist']
            if not metadata.album and download_metadata.get('album'):
                metadata.album = download_metadata['album']
            if not metadata.year and download_metadata.get('year'):
                metadata.year = download_metadata['year']
            if not metadata.genre and download_metadata.get('genre'):
                metadata.genre = download_metadata['genre']
            
            # Generate unique filename for workspace
            original_title_clean = self._clean_filename(download_result['original_title'])
            unique_filename = self._generate_unique_filename(f"{original_title_clean}.mp3", "soundcloud")
            workspace_file_path = os.path.join(self.WORKSPACE_DIR, unique_filename)
            
            # Copy to workspace
            shutil.copy2(downloaded_file_path, workspace_file_path)
            
            return AudioUploadResponse(
                success=True,
                filename=unique_filename,
                metadata=metadata,
                message="SoundCloud audio downloaded and added to workspace successfully",
                platform="soundcloud",
                original_url=url
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading SoundCloud audio: {str(e)}")
        finally:
            # Clean up temporary download
            if downloaded_file_path and os.path.exists(downloaded_file_path):
                try:
                    self.download_service.cleanup_download(downloaded_file_path)
                except Exception:
                    pass
    
    def update_file_metadata(self, stored_filename: str, metadata: AudioMetadata) -> bool:
        """Update metadata for a file in the workspace."""
        file_path = os.path.join(self.WORKSPACE_DIR, stored_filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {stored_filename}")
        
        try:
            # Create updated filename
            updated_filename = self._generate_unique_filename(stored_filename, "updated")
            updated_file_path = os.path.join(self.WORKSPACE_DIR, updated_filename)
            
            # Copy original file
            shutil.copy2(file_path, updated_file_path)
            
            # Update metadata on the copy
            success = self.audio_service.update_metadata(updated_file_path, metadata)
            
            if success:
                return updated_filename
            else:
                # Clean up failed update
                if os.path.exists(updated_file_path):
                    os.unlink(updated_file_path)
                raise HTTPException(status_code=500, detail="Failed to update metadata")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating metadata: {str(e)}")
    
    def get_all_files(self) -> Dict[str, Any]:
        """Get all files in the workspace with their metadata."""
        all_files = []
        
        if not os.path.exists(self.WORKSPACE_DIR):
            return {
                "success": True,
                "files": [],
                "total_files": 0,
                "upload_files": 0,
                "download_files": 0,
                "updated_files": 0
            }
        
        try:
            files_in_dir = os.listdir(self.WORKSPACE_DIR)
            audio_files = [f for f in files_in_dir if f.lower().endswith(self.AUDIO_EXTENSIONS)]
            
            for file in audio_files:
                file_path = os.path.join(self.WORKSPACE_DIR, file)
                if os.path.exists(file_path):
                    # Determine file type and platform
                    platform = 'unknown'
                    file_type = 'unknown'
                    
                    if file.startswith("upload_"):
                        platform = 'upload'
                        file_type = 'uploaded'
                    elif file.startswith("youtube_"):
                        platform = 'youtube'
                        file_type = 'downloaded'
                    elif file.startswith("soundcloud_"):
                        platform = 'soundcloud'
                        file_type = 'downloaded'
                    elif file.startswith("updated_"):
                        platform = 'upload'  # Updated files keep original platform context
                        file_type = 'updated'
                    
                    original_filename = self._extract_original_filename(file)
                    
                    file_info = {
                        'id': f"{file_type}_{file}",
                        'filename': original_filename,
                        'stored_filename': file,
                        'full_path': file_path,
                        'type': file_type,
                        'platform': platform,
                        'mtime': os.path.getmtime(file_path),
                        'size': os.path.getsize(file_path)
                    }
                    all_files.append(file_info)
            
            # Sort by creation timestamp embedded in filename (oldest first to maintain add order)
            # Extract timestamp from filename for proper ordering
            def get_timestamp_from_filename(file_info):
                filename = file_info['stored_filename']
                # Extract timestamp from format: prefix_timestamp_originalname.ext
                if "_" in filename:
                    parts = filename.split("_", 2)
                    if len(parts) >= 2:
                        try:
                            return int(parts[1])  # timestamp is the second part
                        except ValueError:
                            pass
                # Fallback to modification time if timestamp can't be extracted
                return file_info['mtime']
            
            all_files.sort(key=get_timestamp_from_filename)
            
            return {
                "success": True,
                "files": all_files,
                "total_files": len(all_files),
                "uploaded_files": len([f for f in all_files if f['type'] == 'uploaded']),
                "downloaded_files": len([f for f in all_files if f['type'] == 'downloaded']),
                "updated_files": len([f for f in all_files if f['type'] == 'updated'])
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")
    
    def get_file_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get a specific file by its index in the sorted list."""
        files_data = self.get_all_files()
        files = files_data.get('files', [])
        
        if 0 <= index < len(files):
            return files[index]
        return None
    
    def get_file_by_stored_filename(self, stored_filename: str) -> Optional[str]:
        """Get the full path of a file by its stored filename."""
        file_path = os.path.join(self.WORKSPACE_DIR, stored_filename)
        return file_path if os.path.exists(file_path) else None
    
    def create_download_archive(self, file_indices: Optional[List[int]] = None) -> str:
        """Create a zip archive of specified files or all files."""
        files_data = self.get_all_files()
        all_files = files_data.get('files', [])
        
        if not all_files:
            raise HTTPException(status_code=404, detail="No files available for download")
        
        # If specific indices provided, filter files
        if file_indices is not None:
            selected_files = []
            for index in file_indices:
                if 0 <= index < len(all_files):
                    selected_files.append(all_files[index])
            files_to_zip = selected_files
        else:
            files_to_zip = all_files
        
        if not files_to_zip:
            raise HTTPException(status_code=404, detail="No valid files to download")
        
        # Create temporary zip file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.close()
        
        try:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_info in files_to_zip:
                    file_path = file_info['full_path']
                    original_filename = file_info['filename']
                    
                    if os.path.exists(file_path):
                        zip_file.write(file_path, original_filename)
            
            return temp_zip.name
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_zip.name):
                os.unlink(temp_zip.name)
            raise HTTPException(status_code=500, detail=f"Error creating archive: {str(e)}")
    
    def clear_workspace(self) -> Dict[str, Any]:
        """Clear all files from the workspace."""
        cleaned_files = []
        errors = []
        
        if os.path.exists(self.WORKSPACE_DIR):
            try:
                files_in_dir = os.listdir(self.WORKSPACE_DIR)
                audio_files = [f for f in files_in_dir if f.lower().endswith(self.AUDIO_EXTENSIONS)]
                
                for file in audio_files:
                    file_path = os.path.join(self.WORKSPACE_DIR, file)
                    try:
                        os.remove(file_path)
                        cleaned_files.append(file_path)
                    except Exception as e:
                        errors.append(f"Failed to delete {file_path}: {str(e)}")
                        
            except Exception as e:
                errors.append(f"Failed to access workspace directory: {str(e)}")
        
        return {
            "success": True,
            "cleaned_files": cleaned_files,
            "files_count": len(cleaned_files),
            "errors": errors,
            "message": f"Cleared {len(cleaned_files)} files from workspace"
        }
    
    def get_workspace_debug_info(self) -> Dict[str, Any]:
        """Get debug information about the workspace."""
        debug_info = {
            "workspace_directory": self.WORKSPACE_DIR,
            "workspace_exists": os.path.exists(self.WORKSPACE_DIR),
            "working_dir": os.getcwd(),
            "files": [],
            "total_size": 0
        }
        
        if os.path.exists(self.WORKSPACE_DIR):
            try:
                files_in_dir = os.listdir(self.WORKSPACE_DIR)
                for file in files_in_dir:
                    file_path = os.path.join(self.WORKSPACE_DIR, file)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        debug_info["files"].append({
                            "name": file,
                            "size": file_size,
                            "mtime": os.path.getmtime(file_path)
                        })
                        debug_info["total_size"] += file_size
            except Exception as e:
                debug_info["error"] = str(e)
        
        return debug_info
