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

@router.post("/", response_model=AudioUploadResponse)
async def upload_audio_file(files: List[UploadFile] = File(...)):
    """Upload audio files and extract their metadata."""
    # For now, handle just the first file (you can extend this for batch processing)
    file = files[0]
    
    # Validate file type
    allowed_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
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
        
        return AudioUploadResponse(
            success=True,
            filename=file.filename,
            metadata=metadata,
            message="File uploaded and metadata extracted successfully",
            platform="upload"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Always clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

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
        success = audio_service.update_metadata(temp_file_path, audio_metadata)
        
        if success:
            # Create a directory to store updated files
            updated_files_dir = "/tmp/updated_audio_files"
            os.makedirs(updated_files_dir, exist_ok=True)
            
            # Store the updated file with a unique name
            import time
            timestamp = int(time.time())
            updated_filename = f"updated_{timestamp}_{file.filename}"
            updated_file_path = os.path.join(updated_files_dir, updated_filename)
            
            # Copy the updated file to the storage location
            import shutil
            shutil.copy2(temp_file_path, updated_file_path)
            
            print(f"DEBUG: Successfully updated and saved file: {updated_file_path}")
            
            return JSONResponse(content={
                "success": True,
                "message": "Tags updated successfully",
                "filename": file.filename,
                "updated_filename": updated_filename
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
    file_path = os.path.join("/tmp/updated_audio_files", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(path=file_path, filename=filename, media_type='audio/mpeg')

@router.get("/download-latest")
async def download_latest_updated_file():
    """Download the most recently updated audio file."""
    updated_files_dir = "/tmp/updated_audio_files"
    
    if not os.path.exists(updated_files_dir):
        raise HTTPException(status_code=404, detail="No updated files available")
    
    # Find the most recent file
    files = [f for f in os.listdir(updated_files_dir) if f.startswith("updated_")]
    if not files:
        raise HTTPException(status_code=404, detail="No updated files available")
    
    # Sort by creation time (timestamp in filename)
    files.sort(key=lambda x: os.path.getctime(os.path.join(updated_files_dir, x)), reverse=True)
    latest_file = files[0]
    
    file_path = os.path.join(updated_files_dir, latest_file)
    
    # Extract original filename (remove timestamp prefix)
    original_filename = latest_file.split("_", 2)[-1] if "_" in latest_file else latest_file
    
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
        download_result = download_service.download_audio(url, output_format='mp3')
        downloaded_file_path = download_result['file_path']
        
        print(f"DEBUG: Downloaded file to: {downloaded_file_path}")
        
        # Extract metadata using the audio service
        audio_service = AudioService()
        metadata = audio_service.extract_metadata(downloaded_file_path)
        
        # Enhance metadata with info from download
        download_metadata = download_result['metadata']
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
        
        # Create a directory to store downloaded files
        downloaded_files_dir = "/tmp/downloaded_audio_files"
        os.makedirs(downloaded_files_dir, exist_ok=True)
        
        # Store the downloaded file with a unique name
        import time
        timestamp = int(time.time())
        downloaded_filename = f"youtube_{timestamp}_{download_result['original_title'][:50].replace('/', '_')}.mp3"
        stored_file_path = os.path.join(downloaded_files_dir, downloaded_filename)
        
        # Copy the downloaded file to the storage location
        import shutil
        shutil.copy2(downloaded_file_path, stored_file_path)
        
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
<<<<<<< HEAD
=======

@router.post("/download/soundcloud")
async def download_soundcloud_audio(url: str = Form(...)):
    """Download audio from SoundCloud URL and extract metadata."""
    print(f"DEBUG: Received SoundCloud URL: {url}")
    
    download_service = DownloadService()
    downloaded_file_path = None
    
    try:
        # Download the audio
        download_result = download_service.download_audio(url, output_format='mp3')
        downloaded_file_path = download_result['file_path']
        
        print(f"DEBUG: Downloaded file to: {downloaded_file_path}")
        
        # Extract metadata using the audio service
        audio_service = AudioService()
        metadata = audio_service.extract_metadata(downloaded_file_path)
        
        # Enhance metadata with info from download
        download_metadata = download_result['metadata']
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
        
        # Create a directory to store downloaded files
        downloaded_files_dir = "/tmp/downloaded_audio_files"
        os.makedirs(downloaded_files_dir, exist_ok=True)
        
        # Store the downloaded file with a unique name
        import time
        timestamp = int(time.time())
        downloaded_filename = f"soundcloud_{timestamp}_{download_result['original_title'][:50].replace('/', '_')}.mp3"
        stored_file_path = os.path.join(downloaded_files_dir, downloaded_filename)
        
        # Copy the downloaded file to the storage location
        import shutil
        shutil.copy2(downloaded_file_path, stored_file_path)
        
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
>>>>>>> 0bb8875cf171e15a77a5a5f167492537a03f8dc9

@router.post("/download/soundcloud")
async def download_soundcloud_audio(url: str = Form(...)):
    """Download audio from SoundCloud URL and extract metadata."""
    print(f"DEBUG: Received SoundCloud URL: {url}")
    
    download_service = DownloadService()
    downloaded_file_path = None
    
    try:
        # Download the audio
        download_result = download_service.download_audio(url, output_format='mp3')
        downloaded_file_path = download_result['file_path']
        
        print(f"DEBUG: Downloaded file to: {downloaded_file_path}")
        
        # Extract metadata using the audio service
        audio_service = AudioService()
        metadata = audio_service.extract_metadata(downloaded_file_path)
        
        # Enhance metadata with info from download
        download_metadata = download_result['metadata']
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
        
        # Create a directory to store downloaded files
        downloaded_files_dir = "/tmp/downloaded_audio_files"
        os.makedirs(downloaded_files_dir, exist_ok=True)
        
        # Store the downloaded file with a unique name
        import time
        timestamp = int(time.time())
        downloaded_filename = f"soundcloud_{timestamp}_{download_result['original_title'][:50].replace('/', '_')}.mp3"
        stored_file_path = os.path.join(downloaded_files_dir, downloaded_filename)
        
        # Copy the downloaded file to the storage location
        import shutil
        shutil.copy2(downloaded_file_path, stored_file_path)
        
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