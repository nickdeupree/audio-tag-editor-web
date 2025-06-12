"""
Upload router for handling file uploads and audio tag operations.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from app.services.audio_service import AudioService
from app.services.download_service import DownloadService
from models.responses import AudioMetadata, AudioUploadResponse
from typing import List
import tempfile
import os
import json

router = APIRouter(prefix="/upload")

def cleanup_old_cached_files():
    """Clean up old cached files when explicitly requested."""
    cache_dirs = [
        "/tmp/downloaded_audio_files",
        "/app/downloaded_audio_files"
    ]
    
    cleaned_count = 0
    for dir_path in cache_dirs:
        if os.path.exists(dir_path):
            try:
                files_in_dir = os.listdir(dir_path)
                audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
                audio_files = [f for f in files_in_dir if f.lower().endswith(audio_extensions)]
                
                for file in audio_files:
                    file_path = os.path.join(dir_path, file)
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                        print(f"DEBUG: Removed cached file: {file_path}")
                    except Exception as e:
                        print(f"DEBUG: Failed to remove cached file {file_path}: {e}")
            except Exception as e:
                print(f"DEBUG: Failed to clean cache directory {dir_path}: {e}")
    
    return cleaned_count

@router.post("/", response_model=AudioUploadResponse)
async def upload_audio_file(files: List[UploadFile] = File(...)):
    """Upload audio files and extract their metadata."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Handle multiple files - return metadata for all of them
    all_metadata = []
    
    for file in files:
        # Validate file type
        allowed_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format for {file.filename}. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        temp_file_path = None
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Extract metadata using the audio service
            audio_service = AudioService()
            metadata = audio_service.extract_metadata(temp_file_path)
            
            all_metadata.append({
                'filename': file.filename,
                'metadata': metadata
            })
            
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")
        finally:
            # Always clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
    
    # Return the first file's info for compatibility, but include all metadata
    first_file = files[0]
    first_metadata = all_metadata[0]['metadata'] if all_metadata else None
    
    return AudioUploadResponse(
        success=True,
        filename=first_file.filename,
        metadata=first_metadata,
        message=f"{len(files)} file(s) uploaded and metadata extracted successfully",
        platform="upload",
        all_files_metadata=all_metadata  # Include all files metadata
    )

@router.post("/update-tags")
async def update_audio_tags(
    file: UploadFile = File(...), 
    metadata: str = Form(...)  # Change to receive metadata as form field
):
    """Update audio file tags with new metadata and store the updated file."""
    print(f"DEBUG: Received file: {file.filename}")
    print(f"DEBUG: File content type: {file.content_type}")
    print(f"DEBUG: Raw metadata string: {metadata}")
    
    if not file.filename.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    temp_file_path = None
    try:
        # Parse metadata JSON
        try:
            metadata_dict = json.loads(metadata)
            print(f"DEBUG: Parsed metadata: {metadata_dict}")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid metadata JSON: {str(e)}")
        
        # Validate metadata structure
        if not isinstance(metadata_dict, dict):
            raise HTTPException(status_code=400, detail="Metadata must be a JSON object")
        
        # Create AudioMetadata object with proper null handling
        audio_metadata = AudioMetadata(
            title=metadata_dict.get('title') if metadata_dict.get('title') else None,
            artist=metadata_dict.get('artist') if metadata_dict.get('artist') else None,
            album=metadata_dict.get('album') if metadata_dict.get('album') else None,
            genre=metadata_dict.get('genre') if metadata_dict.get('genre') else None,
            year=metadata_dict.get('year') if metadata_dict.get('year') else None,
            cover_art=metadata_dict.get('cover_art') if metadata_dict.get('cover_art') else None,
            cover_art_mime_type=metadata_dict.get('cover_art_mime_type') if metadata_dict.get('cover_art_mime_type') else None
        )
        
        print(f"DEBUG: Created AudioMetadata object: {audio_metadata}")
          # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        print(f"DEBUG: Created temp file: {temp_file_path}")
        
        # Update metadata
        audio_service = AudioService()
        print(f"DEBUG: About to call update_metadata with file: {temp_file_path}")
        print(f"DEBUG: File exists: {os.path.exists(temp_file_path)}")
        print(f"DEBUG: File size: {os.path.getsize(temp_file_path) if os.path.exists(temp_file_path) else 'N/A'}")
        
        success = audio_service.update_metadata(temp_file_path, audio_metadata)
        print(f"DEBUG: update_metadata returned: {success}")
        
        if success:
            # Create a directory to store updated files
            # Try multiple locations in case /tmp has issues
            possible_dirs = [
                "/tmp/updated_audio_files",
                "/app/updated_audio_files",  # Common for containerized environments
                "./updated_audio_files",     # Relative to working directory
                os.path.join(os.getcwd(), "updated_audio_files")  # Absolute path from working dir
            ]
            
            updated_files_dir = None
            for dir_path in possible_dirs:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    # Test write permissions
                    test_file = os.path.join(dir_path, "test_write.tmp")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    updated_files_dir = dir_path
                    print(f"DEBUG: Successfully using directory: {updated_files_dir}")
                    break
                except Exception as e:
                    print(f"DEBUG: Failed to use directory {dir_path}: {e}")
                    continue
            
            if not updated_files_dir:
                raise HTTPException(status_code=500, detail="Could not create writable directory for updated files")
            
            print(f"DEBUG: Creating/checking directory: {updated_files_dir}")
            print(f"DEBUG: Directory created/exists: {os.path.exists(updated_files_dir)}")
            
            # Store the updated file with a unique name
            import time
            timestamp = int(time.time())
            updated_filename = f"updated_{timestamp}_{file.filename}"
            updated_file_path = os.path.join(updated_files_dir, updated_filename)
            
            print(f"DEBUG: About to copy from {temp_file_path} to {updated_file_path}")
            # Copy the updated file to the storage location
            import shutil
            shutil.copy2(temp_file_path, updated_file_path)
            
            print(f"DEBUG: Copy completed. File exists: {os.path.exists(updated_file_path)}")
            print(f"DEBUG: Copied file size: {os.path.getsize(updated_file_path) if os.path.exists(updated_file_path) else 'N/A'}")
            print(f"DEBUG: Successfully updated and saved file: {updated_file_path}")
            
            # List all files in the directory for debugging
            all_files_in_dir = os.listdir(updated_files_dir)
            print(f"DEBUG: All files in {updated_files_dir}: {all_files_in_dir}")
            
            return JSONResponse(content={
                "success": True,
                "message": "Tags updated successfully",
                "filename": file.filename,
                "updated_filename": updated_filename,
                "storage_directory": updated_files_dir  # Include this for debugging
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to update tags")
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating file: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

@router.post("/cover-art")
async def update_cover_art(
    audio_file: UploadFile = File(...),
    cover_file: UploadFile = File(...)
):
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
        audio_service = AudioService()
        success = audio_service.update_cover_art(audio_temp_path, cover_b64, mime_type)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "Cover art updated successfully",
                "filename": audio_file.filename
            })
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

@router.get("/cover-art/{filename}")
async def get_cover_art(filename: str):
    """Extract and return cover art from an audio file."""
    # This endpoint would need to be enhanced to work with stored files
    # For now, return a placeholder response
    return JSONResponse(content={
        "message": "Cover art extraction endpoint - implementation depends on your file storage strategy"
    })

@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve the updated audio file for download."""
    # Construct the file path (this should match the storage location in the update-tags endpoint)
    updated_files_dir = "/tmp/updated_audio_files"
    file_path = os.path.join(updated_files_dir, filename)
    
    print(f"DEBUG: Looking for file: {file_path}")
    print(f"DEBUG: Directory exists: {os.path.exists(updated_files_dir)}")
    
    if os.path.exists(updated_files_dir):
        print(f"DEBUG: Files in directory: {os.listdir(updated_files_dir)}")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    return FileResponse(path=file_path, filename=filename, media_type='audio/mpeg')

@router.get("/download-latest")
async def download_latest_updated_file():
    """Download the most recently updated audio file."""
    # Prioritized locations - check updated files first, then downloads
    priority_dirs = [
        "/tmp/updated_audio_files",     # Highest priority - edited files
        "/app/updated_audio_files",
        "./updated_audio_files",
        os.path.join(os.getcwd(), "updated_audio_files")
    ]
    
    fallback_dirs = [
        "/tmp/downloaded_audio_files",  # Fallback - original downloads
        "/app/downloaded_audio_files",
        "./downloaded_audio_files",
        os.path.join(os.getcwd(), "downloaded_audio_files")
    ]
    
    audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
    
    # First, check priority directories for any files
    priority_files = []
    for dir_path in priority_dirs:
        if os.path.exists(dir_path):
            files_in_dir = os.listdir(dir_path)
            audio_files = [f for f in files_in_dir if f.lower().endswith(audio_extensions)]
            print(f"DEBUG: Checking priority dir {dir_path} - audio files: {audio_files}")
            
            for file in audio_files:
                file_path = os.path.join(dir_path, file)
                if os.path.exists(file_path):
                    file_info = {
                        'filename': file,
                        'full_path': file_path,
                        'directory': dir_path,
                        'mtime': os.path.getmtime(file_path),
                        'priority': True
                    }
                    priority_files.append(file_info)
                    print(f"DEBUG: Found priority file: {file} in {dir_path}, mtime: {file_info['mtime']}")
        else:
            print(f"DEBUG: Priority directory {dir_path} does not exist")
    
    # If we found files in priority directories, use those
    if priority_files:
        print(f"DEBUG: Found {len(priority_files)} files in priority directories, using newest")
        priority_files.sort(key=lambda x: x['mtime'], reverse=True)
        latest_file_info = priority_files[0]
    else:
        # Otherwise, check fallback directories
        print("DEBUG: No files in priority directories, checking fallback directories")
        fallback_files = []
        for dir_path in fallback_dirs:
            if os.path.exists(dir_path):
                files_in_dir = os.listdir(dir_path)
                audio_files = [f for f in files_in_dir if f.lower().endswith(audio_extensions)]
                print(f"DEBUG: Checking fallback dir {dir_path} - audio files: {audio_files}")
                
                for file in audio_files:
                    file_path = os.path.join(dir_path, file)
                    if os.path.exists(file_path):
                        file_info = {
                            'filename': file,
                            'full_path': file_path,
                            'directory': dir_path,
                            'mtime': os.path.getmtime(file_path),
                            'priority': False
                        }
                        fallback_files.append(file_info)
                        print(f"DEBUG: Found fallback file: {file} in {dir_path}, mtime: {file_info['mtime']}")
            else:
                print(f"DEBUG: Fallback directory {dir_path} does not exist")
        
        if not fallback_files:
            print("DEBUG: No audio files found in any directory")
            # List what we found for debugging
            all_dirs = priority_dirs + fallback_dirs
            for dir_path in all_dirs:
                if os.path.exists(dir_path):
                    all_files = os.listdir(dir_path)
                    print(f"DEBUG: {dir_path} contents: {all_files}")
            raise HTTPException(status_code=404, detail="No audio files available for download")
        
        fallback_files.sort(key=lambda x: x['mtime'], reverse=True)
        latest_file_info = fallback_files[0]
    
    print(f"DEBUG: Latest file selected: {latest_file_info['filename']} from {latest_file_info['directory']}")
    print(f"DEBUG: File modification time: {latest_file_info['mtime']}")
    
    file_path = latest_file_info['full_path']
    filename = latest_file_info['filename']
    
    # Extract original filename (remove timestamp prefix if it exists)
    if filename.startswith(("updated_", "youtube_", "soundcloud_")) and "_" in filename:
        # Format: prefix_timestamp_originalname.mp3
        parts = filename.split("_", 2)
        original_filename = parts[2] if len(parts) > 2 else filename
    else:
        original_filename = filename
    
    print(f"DEBUG: Serving file: {file_path} as {original_filename}")
    print(f"DEBUG: File exists: {os.path.exists(file_path)}")
    print(f"DEBUG: File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'}")
    
    return FileResponse(
        path=file_path, 
        filename=original_filename,
        media_type='application/octet-stream'
    )

@router.post("/download/youtube")
async def download_youtube_audio(url: str = Form(...)):
    """Download audio from YouTube URL and extract metadata."""
    print(f"DEBUG: Received YouTube URL: {url}")
    
    download_service = DownloadService()
    downloaded_file_path = None
    
    try:
        # Download the audio
        print(f"DEBUG: Starting YouTube audio download...")
        download_result = download_service.download_audio(url, output_format='mp3')
        downloaded_file_path = download_result['file_path']
        
        print(f"DEBUG: Downloaded file to: {downloaded_file_path}")
        print(f"DEBUG: Downloaded file exists: {os.path.exists(downloaded_file_path) if downloaded_file_path else 'N/A'}")
        print(f"DEBUG: Downloaded file size: {os.path.getsize(downloaded_file_path) if downloaded_file_path and os.path.exists(downloaded_file_path) else 'N/A'}")
        
        # Extract metadata using the audio service
        audio_service = AudioService()
        metadata = audio_service.extract_metadata(downloaded_file_path)
        print(f"DEBUG: Extracted metadata: {metadata}")
        
        # Enhance metadata with info from download
        download_metadata = download_result['metadata']
        print(f"DEBUG: Download metadata: {download_metadata}")
        
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
        
        print(f"DEBUG: Enhanced metadata: {metadata}")
        
        # Create a directory to store downloaded files
        downloaded_files_dir = "/tmp/downloaded_audio_files"
        print(f"DEBUG: Creating downloaded files directory: {downloaded_files_dir}")
        os.makedirs(downloaded_files_dir, exist_ok=True)
        print(f"DEBUG: Directory created/exists: {os.path.exists(downloaded_files_dir)}")
        
        # Store the downloaded file with a unique name
        import time
        timestamp = int(time.time())
        original_title_clean = download_result['original_title'][:50].replace('/', '_').replace('\\', '_').replace(':', '_').replace('?', '_').replace('*', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('"', '_')
        downloaded_filename = f"youtube_{timestamp}_{original_title_clean}.mp3"
        stored_file_path = os.path.join(downloaded_files_dir, downloaded_filename)
        
        print(f"DEBUG: Storing file as: {stored_file_path}")
        
        # Copy the downloaded file to the storage location
        import shutil
        shutil.copy2(downloaded_file_path, stored_file_path)
        
        print(f"DEBUG: File copied successfully. Stored file exists: {os.path.exists(stored_file_path)}")
        print(f"DEBUG: Stored file size: {os.path.getsize(stored_file_path) if os.path.exists(stored_file_path) else 'N/A'}")
        
        # List all files in the directory
        all_files_in_dir = os.listdir(downloaded_files_dir)
        print(f"DEBUG: All files in {downloaded_files_dir}: {all_files_in_dir}")
        
        return AudioUploadResponse(
            success=True,
            filename=downloaded_filename,
            metadata=metadata,
            message="YouTube audio downloaded and metadata extracted successfully",
            platform="youtube",
            original_url=url
        )
        
    except Exception as e:
        print(f"DEBUG: Download error: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading YouTube audio: {str(e)}")
    finally:
        # Clean up temporary download file
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            try:
                download_service.cleanup_download(downloaded_file_path)
            except Exception:
                pass

@router.post("/download/soundcloud")
async def download_soundcloud_audio(url: str = Form(...)):
    """Download audio from SoundCloud URL and extract metadata."""
    print(f"DEBUG: Received SoundCloud URL: {url}")
    
    download_service = DownloadService()
    downloaded_file_path = None
    
    try:
        # Download the audio
        print(f"DEBUG: Starting SoundCloud audio download...")
        download_result = download_service.download_audio(url, output_format='mp3')
        downloaded_file_path = download_result['file_path']
        
        print(f"DEBUG: Downloaded file to: {downloaded_file_path}")
        print(f"DEBUG: Downloaded file exists: {os.path.exists(downloaded_file_path) if downloaded_file_path else 'N/A'}")
        print(f"DEBUG: Downloaded file size: {os.path.getsize(downloaded_file_path) if downloaded_file_path and os.path.exists(downloaded_file_path) else 'N/A'}")
        
        # Extract metadata using the audio service
        audio_service = AudioService()
        metadata = audio_service.extract_metadata(downloaded_file_path)
        print(f"DEBUG: Extracted metadata: {metadata}")
        
        # Enhance metadata with info from download
        download_metadata = download_result['metadata']
        print(f"DEBUG: Download metadata: {download_metadata}")
        
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
        
        print(f"DEBUG: Enhanced metadata: {metadata}")
        
        # Create a directory to store downloaded files
        downloaded_files_dir = "/tmp/downloaded_audio_files"
        print(f"DEBUG: Creating downloaded files directory: {downloaded_files_dir}")
        os.makedirs(downloaded_files_dir, exist_ok=True)
        print(f"DEBUG: Directory created/exists: {os.path.exists(downloaded_files_dir)}")
        
        # Store the downloaded file with a unique name
        import time
        timestamp = int(time.time())
        original_title_clean = download_result['original_title'][:50].replace('/', '_').replace('\\', '_').replace(':', '_').replace('?', '_').replace('*', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('"', '_')
        downloaded_filename = f"soundcloud_{timestamp}_{original_title_clean}.mp3"
        stored_file_path = os.path.join(downloaded_files_dir, downloaded_filename)
        
        print(f"DEBUG: Storing file as: {stored_file_path}")
        
        # Copy the downloaded file to the storage location
        import shutil
        shutil.copy2(downloaded_file_path, stored_file_path)
        
        print(f"DEBUG: File copied successfully. Stored file exists: {os.path.exists(stored_file_path)}")
        print(f"DEBUG: Stored file size: {os.path.getsize(stored_file_path) if os.path.exists(stored_file_path) else 'N/A'}")
        
        # List all files in the directory
        all_files_in_dir = os.listdir(downloaded_files_dir)
        print(f"DEBUG: All files in {downloaded_files_dir}: {all_files_in_dir}")
        
        return AudioUploadResponse(
            success=True,
            filename=downloaded_filename,
            metadata=metadata,
            message="SoundCloud audio downloaded and metadata extracted successfully",
            platform="soundcloud",
            original_url=url
        )
        
    except Exception as e:
        print(f"DEBUG: Download error: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading SoundCloud audio: {str(e)}")
    finally:
        # Clean up temporary download file
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            try:
                download_service.cleanup_download(downloaded_file_path)
            except Exception:
                pass

@router.get("/debug/files")
async def debug_files():
    """Debug endpoint to check file system state."""
    possible_dirs = [
        "/tmp/updated_audio_files",
        "/app/updated_audio_files",
        "./updated_audio_files",
        os.path.join(os.getcwd(), "updated_audio_files")
    ]
    
    debug_info = {
        "possible_directories": [],
        "working_dir": os.getcwd(),
        "user_info": {},
        "tmp_contents": []
    }
    
    for dir_path in possible_dirs:
        dir_info = {
            "path": dir_path,
            "exists": os.path.exists(dir_path),
            "files": [],
            "error": None
        }
        
        try:
            if os.path.exists(dir_path):
                dir_info["files"] = os.listdir(dir_path)
                dir_stat = os.stat(dir_path)
                dir_info["permissions"] = oct(dir_stat.st_mode)
                dir_info["owner"] = dir_stat.st_uid
        except Exception as e:
            dir_info["error"] = str(e)
            
        debug_info["possible_directories"].append(dir_info)
    
    try:
        debug_info["tmp_contents"] = os.listdir("/tmp")[:20]  # Limit to first 20 items
    except Exception as e:
        debug_info["tmp_error"] = str(e)
    
    try:
        import getpass
        debug_info["user_info"]["username"] = getpass.getuser()
    except Exception as e:
        debug_info["user_info"]["error"] = str(e)
    
    return JSONResponse(content=debug_info)

@router.get("/test-download")
async def test_download_service():
    """Test the download service functionality."""
    try:
        download_service = DownloadService()
        test_result = download_service.test_ytdl_functionality()
        
        return JSONResponse(content={
            "success": test_result['success'],
            "message": "Download service test completed",
            "test_result": test_result
        })
        
    except Exception as e:
        print(f"DEBUG: Test error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Download service test failed: {str(e)}"
            }
        )

@router.get("/download-all")
async def download_all_updated_files():
    """Download all audio files as a zip archive."""
    import zipfile
    import tempfile
    import shutil
    
    # Prioritized locations - check updated files first, then downloads
    priority_dirs = [
        "/tmp/updated_audio_files",     # Highest priority - edited files
        "/app/updated_audio_files",
        "./updated_audio_files",
        os.path.join(os.getcwd(), "updated_audio_files")
    ]
    
    fallback_dirs = [
        "/tmp/downloaded_audio_files",  # Fallback - original downloads
        "/app/downloaded_audio_files",
        "./downloaded_audio_files",
        os.path.join(os.getcwd(), "downloaded_audio_files")
    ]
    
    audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
    all_audio_files = []
      # First, collect files from priority directories (updated files)
    for dir_path in priority_dirs:
        if os.path.exists(dir_path):
            files_in_dir = os.listdir(dir_path)
            audio_files = [f for f in files_in_dir if f.lower().endswith(audio_extensions)]
            print(f"DEBUG: Checking priority dir {dir_path} for download-all - audio files: {audio_files}")
            
            for file in audio_files:
                file_path = os.path.join(dir_path, file)
                if os.path.exists(file_path):
                    all_audio_files.append({
                        'filename': file,
                        'full_path': file_path,
                        'directory': dir_path,
                        'priority': True
                    })
        else:
            print(f"DEBUG: Priority directory {dir_path} does not exist")
    
    # Also collect files from fallback directories (downloaded files) - ALWAYS include these
    print("DEBUG: Checking fallback directories for additional files")
    for dir_path in fallback_dirs:
        if os.path.exists(dir_path):
            files_in_dir = os.listdir(dir_path)
            audio_files = [f for f in files_in_dir if f.lower().endswith(audio_extensions)]
            print(f"DEBUG: Checking fallback dir {dir_path} for download-all - audio files: {audio_files}")
            
            for file in audio_files:
                file_path = os.path.join(dir_path, file)
                if os.path.exists(file_path):
                    all_audio_files.append({
                        'filename': file,
                        'full_path': file_path,
                        'directory': dir_path,
                        'priority': False
                    })
        else:
            print(f"DEBUG: Fallback directory {dir_path} does not exist")
    
    if not all_audio_files:
        print("DEBUG: No audio files found in any directory for download-all")
        # List what we found for debugging
        all_dirs = priority_dirs + fallback_dirs
        for dir_path in all_dirs:
            if os.path.exists(dir_path):
                all_files = os.listdir(dir_path)
                print(f"DEBUG: {dir_path} contents: {all_files}")
        raise HTTPException(status_code=404, detail="No audio files available for download")    
    print(f"DEBUG: Found {len(all_audio_files)} total audio files for zip")
    
    # Create a temporary zip file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip.close()
    
    try:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_info in all_audio_files:
                file = file_info['filename']
                file_path = file_info['full_path']
                
                # Extract original filename (remove timestamp prefix if it exists)
                if file.startswith(("updated_", "youtube_", "soundcloud_")) and "_" in file:
                    parts = file.split("_", 2)
                    original_filename = parts[2] if len(parts) > 2 else file
                else:
                    original_filename = file
                
                print(f"DEBUG: Adding to zip: {file_path} as {original_filename}")
                zip_file.write(file_path, original_filename)
        
        print(f"DEBUG: Created zip file: {temp_zip.name}")
        
        return FileResponse(
            path=temp_zip.name,
            filename="updated_audio_files.zip",
            media_type='application/zip'
        )
    except Exception as e:
        print(f"DEBUG: Error creating zip: {e}")
        # Clean up temp file if something goes wrong
        if os.path.exists(temp_zip.name):
            os.unlink(temp_zip.name)
        raise HTTPException(status_code=500, detail=f"Error creating zip file: {str(e)}")

@router.delete("/cleanup/downloads")
async def cleanup_old_downloads():
    """Clean up old downloaded files to prevent cache conflicts."""
    cleanup_dirs = [
        "/tmp/downloaded_audio_files",
        "/app/downloaded_audio_files",
        "./downloaded_audio_files",
        os.path.join(os.getcwd(), "downloaded_audio_files")
    ]
    
    cleaned_files = []
    errors = []
    
    for dir_path in cleanup_dirs:
        if os.path.exists(dir_path):
            try:
                files_in_dir = os.listdir(dir_path)
                audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
                audio_files = [f for f in files_in_dir if f.lower().endswith(audio_extensions)]
                
                print(f"DEBUG: Cleaning up {len(audio_files)} files from {dir_path}")
                
                for file in audio_files:
                    file_path = os.path.join(dir_path, file)
                    try:
                        os.remove(file_path)
                        cleaned_files.append(file_path)
                        print(f"DEBUG: Deleted {file_path}")
                    except Exception as e:
                        error_msg = f"Failed to delete {file_path}: {str(e)}"
                        errors.append(error_msg)
                        print(f"DEBUG: {error_msg}")
                        
            except Exception as e:
                error_msg = f"Failed to access directory {dir_path}: {str(e)}"
                errors.append(error_msg)
                print(f"DEBUG: {error_msg}")
    
    return {
        "success": True,
        "cleaned_files": cleaned_files,
        "files_count": len(cleaned_files),
        "errors": errors,
        "message": f"Cleaned up {len(cleaned_files)} cached files"
    }

@router.post("/clear-cache")
async def clear_download_cache():
    """Clear cached downloads to start fresh."""
    cleaned_count = cleanup_old_cached_files()
    
    return {
        "success": True,
        "message": f"Cleared {cleaned_count} cached files",
        "files_cleaned": cleaned_count
    }

@router.get("/files/all")
async def get_all_files():
    """Get all available audio files (both downloaded and uploaded) for frontend pagination."""
    priority_dirs = [
        "/tmp/updated_audio_files",     # Updated files (edited metadata)
        "/app/updated_audio_files",
        "./updated_audio_files",
        os.path.join(os.getcwd(), "updated_audio_files")
    ]
    
    download_dirs = [
        "/tmp/downloaded_audio_files",  # Downloaded files (YouTube/SoundCloud)
        "/app/downloaded_audio_files",
        "./downloaded_audio_files",
        os.path.join(os.getcwd(), "downloaded_audio_files")
    ]
    
    audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
    all_files = []
    
    # Collect updated/edited files
    for dir_path in priority_dirs:
        if os.path.exists(dir_path):
            files_in_dir = os.listdir(dir_path)
            audio_files = [f for f in files_in_dir if f.lower().endswith(audio_extensions)]
            
            for file in audio_files:
                file_path = os.path.join(dir_path, file)
                if os.path.exists(file_path):
                    # Extract original filename
                    original_filename = file
                    if file.startswith("updated_") and "_" in file:
                        parts = file.split("_", 2)
                        original_filename = parts[2] if len(parts) > 2 else file
                    
                    file_info = {
                        'id': f"updated_{file}",
                        'filename': original_filename,
                        'stored_filename': file,
                        'full_path': file_path,
                        'directory': dir_path,
                        'type': 'updated',
                        'platform': 'upload',
                        'mtime': os.path.getmtime(file_path),
                        'size': os.path.getsize(file_path)
                    }
                    all_files.append(file_info)
    
    # Collect downloaded files (YouTube/SoundCloud)
    for dir_path in download_dirs:
        if os.path.exists(dir_path):
            files_in_dir = os.listdir(dir_path)
            audio_files = [f for f in files_in_dir if f.lower().endswith(audio_extensions)]
            
            for file in audio_files:
                file_path = os.path.join(dir_path, file)
                if os.path.exists(file_path):
                    # Extract original filename and platform
                    original_filename = file
                    platform = 'download'
                    
                    if file.startswith("youtube_") and "_" in file:
                        parts = file.split("_", 2)
                        original_filename = parts[2] if len(parts) > 2 else file
                        platform = 'youtube'
                    elif file.startswith("soundcloud_") and "_" in file:
                        parts = file.split("_", 2)
                        original_filename = parts[2] if len(parts) > 2 else file
                        platform = 'soundcloud'
                    
                    file_info = {
                        'id': f"download_{file}",
                        'filename': original_filename,
                        'stored_filename': file,
                        'full_path': file_path,
                        'directory': dir_path,
                        'type': 'downloaded',
                        'platform': platform,
                        'mtime': os.path.getmtime(file_path),
                        'size': os.path.getsize(file_path)
                    }
                    all_files.append(file_info)
    
    # Sort by modification time (newest first)
    all_files.sort(key=lambda x: x['mtime'], reverse=True)
    
    return {
        "success": True,
        "files": all_files,
        "total_files": len(all_files),
        "updated_files": len([f for f in all_files if f['type'] == 'updated']),
        "downloaded_files": len([f for f in all_files if f['type'] == 'downloaded'])
    }