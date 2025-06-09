"""
Upload router for handling file uploads and audio tag operations.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from services.audio_service import AudioService
from services.downloader_service import DownloaderService
from models.responses import AudioMetadata, AudioUploadResponse, AudioUpdateRequest
from typing import List
import tempfile
import os
import json
import io
import shutil
import zipfile
import time
from loguru import logger

router = APIRouter(prefix="/upload")

@router.post("/")
async def upload_audio_files(files: List[UploadFile] = File(...)):
    """Upload audio files and extract their metadata."""
    # Clear any existing cached files when new files are uploaded
    updated_files_dir = "/tmp/updated_audio_files"
    if os.path.exists(updated_files_dir):
        shutil.rmtree(updated_files_dir)
        logger.info("Cleared cached updated files")
    
    allowed_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')
    audio_service = AudioService()
    results = []
    
    for file in files:
        # Validate file type
        if not file.filename.lower().endswith(allowed_extensions):
            results.append({
                "success": False,
                "filename": file.filename,
                "error": f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            })
            continue
        
        temp_file_path = None
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name            # Extract metadata using the audio service
            metadata = audio_service.extract_metadata(temp_file_path)
            
            # Convert metadata to dict for JSON serialization
            metadata_dict = metadata.model_dump() if hasattr(metadata, 'model_dump') else metadata.dict()
            
            results.append({
                "success": True,
                "filename": file.filename,
                "metadata": metadata_dict
            })
            
        except ValueError as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": str(e)
            })
        except Exception as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": f"Error processing file: {str(e)}"
            })
        finally:
            # Always clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
    
    return JSONResponse(content={
        "success": True,
        "files": results,
        "message": f"Processed {len(files)} file(s)"
    })

@router.post("/update-tags")
async def update_audio_tags(
    file: UploadFile = File(...),
    metadata: str = Form(...)
):
    """Update audio file tags with new metadata and store the updated file."""
    temp_file_path = None
    try:
        logger.debug(f"Received file: {file.filename}")
        logger.debug(f"File content type: {file.content_type}")
        logger.debug(f"Raw metadata string: {metadata}")
        
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
            logger.debug(f"Parsed metadata: {metadata_dict}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON metadata: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid metadata JSON: {str(e)}")
        
        # Create AudioMetadata object
        try:
            audio_metadata = AudioMetadata(**metadata_dict)
            logger.debug(f"Created AudioMetadata object: {audio_metadata}")
        except Exception as e:
            logger.error(f"Error creating AudioMetadata object: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid metadata format: {str(e)}")
        
        # Validate file
        if not file.filename:
            logger.error("No filename provided")
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.mp3', '.wav', '.flac', '.m4a', '.ogg']:
            logger.error(f"Unsupported file format: {file_extension}")
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")
        
        # Read file content
        try:
            content = await file.read()
            logger.debug(f"File size: {len(content)} bytes")
            
            if len(content) == 0:
                logger.error("File content is empty")
                raise HTTPException(status_code=400, detail="File content is empty")
                
        except Exception as e:
            logger.error(f"Error reading file content: {e}")
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
        
        # Create temp file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file_path = temp_file.name
                logger.debug(f"Created temp file: {temp_file_path}")
                temp_file.write(content)
                temp_file.flush()
                
            # Verify temp file
            if not os.path.exists(temp_file_path):
                logger.error("Temp file was not created")
                raise HTTPException(status_code=500, detail="Failed to create temporary file")
                
            temp_file_size = os.path.getsize(temp_file_path)
            logger.debug(f"Temp file size: {temp_file_size} bytes")
            
            if temp_file_size == 0:
                logger.error("Temp file is empty")
                raise HTTPException(status_code=400, detail="Temporary file is empty")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating temp file: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating temporary file: {str(e)}")
          # Update metadata
        try:
            logger.debug("Attempting to update metadata...")
            audio_service = AudioService()
            success = audio_service.update_metadata(temp_file_path, audio_metadata)
            
            if not success:
                logger.error("Metadata update failed")
                raise HTTPException(status_code=500, detail="Failed to update metadata")
                
            logger.debug("Metadata update successful")
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            if "corrupted" in str(e).lower() or "empty" in str(e).lower():
                raise HTTPException(status_code=400, detail=str(e))
            else:
                raise HTTPException(status_code=500, detail=f"Error updating metadata: {str(e)}")
        
        # Read updated file
        try:
            with open(temp_file_path, 'rb') as updated_file:
                updated_content = updated_file.read()
                
            if len(updated_content) == 0:
                logger.error("Updated file is empty")
                raise HTTPException(status_code=500, detail="Updated file is empty")
                
            logger.debug(f"Updated file size: {len(updated_content)} bytes")
            
        except Exception as e:
            logger.error(f"Error reading updated file: {e}")
            raise HTTPException(status_code=500, detail=f"Error reading updated file: {str(e)}")
        
        # Return response
        return StreamingResponse(
            io.BytesIO(updated_content),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename={file.filename}"}
        )
        
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_audio_tags: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Cleaned up temp file: {temp_file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {cleanup_error}")

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
async def download_specific_updated_file(filename: str):
    """Download a specific updated audio file by filename."""
    updated_files_dir = "/tmp/updated_audio_files"
    
    if not os.path.exists(updated_files_dir):
        raise HTTPException(status_code=404, detail="No updated files available")
    
    # Find the file with the given filename
    files = [f for f in os.listdir(updated_files_dir) if f.startswith("updated_") and filename in f]
    if not files:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    
    # Get the most recent version if multiple exist
    files.sort(key=lambda x: os.path.getctime(os.path.join(updated_files_dir, x)), reverse=True)
    target_file = files[0]
    
    file_path = os.path.join(updated_files_dir, target_file)
    
    # Extract original filename (remove timestamp prefix)
    original_filename = target_file.split("_", 2)[-1] if "_" in target_file else target_file
    return FileResponse(
        path=file_path, 
        filename=original_filename,
        media_type='application/octet-stream'
    )

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

@router.get("/download-all")
async def download_all_updated_files():
    """Download all updated audio files as a ZIP archive."""
    updated_files_dir = "/tmp/updated_audio_files"
    
    if not os.path.exists(updated_files_dir):
        raise HTTPException(status_code=404, detail="No updated files available")
    
    # Find all updated files
    files = [f for f in os.listdir(updated_files_dir) if f.startswith("updated_")]
    if not files:
        raise HTTPException(status_code=404, detail="No updated files available")
    
    # Create a temporary ZIP file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as zip_temp:
        zip_path = zip_temp.name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                file_path = os.path.join(updated_files_dir, file)
                if os.path.exists(file_path):
                    # Extract original filename (remove timestamp prefix)
                    original_filename = file.split("_", 2)[-1] if "_" in file else file
                    zipf.write(file_path, original_filename)
    return FileResponse(
        path=zip_path,
        filename="updated_audio_files.zip",
        media_type='application/zip'
    )

@router.delete("/clear-cache")
async def clear_updated_files_cache():
    """Clear all cached updated files."""
    updated_files_dir = "/tmp/updated_audio_files"
    
    if os.path.exists(updated_files_dir):
        shutil.rmtree(updated_files_dir)
        return JSONResponse(content={
            "success": True,
            "message": "Cache cleared successfully"
        })
    else:
        return JSONResponse(content={
            "success": True,
            "message": "No cache to clear"
        })

@router.post("/download-youtube")
async def download_youtube_video(url: str = Form(...)):
    """Download audio from a YouTube video."""
    logger.debug(f"Received YouTube URL: {url}")
    
    if not url:
        raise HTTPException(status_code=400, detail="YouTube URL is required")
    
    # Download audio using the downloader service
    downloader_service = DownloaderService()
    try:
        # Download audio as MP3 (you can change the format if needed)
        file_path = await downloader_service.download_youtube_audio(url, format='mp3')
        
        if not file_path:
            raise HTTPException(status_code=500, detail="Failed to download audio from YouTube")
        
        # Extract metadata
        audio_service = AudioService()
        metadata = audio_service.extract_metadata(file_path)
        
        # Convert metadata to dict for JSON serialization
        metadata_dict = metadata.model_dump() if hasattr(metadata, 'model_dump') else metadata.dict()
        
        return JSONResponse(content={
            "success": True,
            "message": "YouTube audio downloaded successfully",
            "metadata": metadata_dict
        })
    except Exception as e:
        logger.error(f"Error downloading YouTube audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading YouTube audio: {str(e)}")

@router.post("/download-soundcloud")
async def download_soundcloud_track(url: str = Form(...)):
    """Download audio from a SoundCloud track."""
    logger.debug(f"Received SoundCloud URL: {url}")
    
    if not url:
        raise HTTPException(status_code=400, detail="SoundCloud URL is required")
    
    # Download audio using the downloader service
    downloader_service = DownloaderService()
    try:
        # Download audio as MP3 (you can change the format if needed)
        file_path = await downloader_service.download_soundcloud_audio(url, format='mp3')
        
        if not file_path:
            raise HTTPException(status_code=500, detail="Failed to download audio from SoundCloud")
        
        # Extract metadata
        audio_service = AudioService()
        metadata = audio_service.extract_metadata(file_path)
        
        # Convert metadata to dict for JSON serialization
        metadata_dict = metadata.model_dump() if hasattr(metadata, 'model_dump') else metadata.dict()
        
        return JSONResponse(content={
            "success": True,
            "message": "SoundCloud audio downloaded successfully",
            "metadata": metadata_dict
        })
    except Exception as e:
        logger.error(f"Error downloading SoundCloud audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading SoundCloud audio: {str(e)}")

@router.post("/download-from-url")
async def download_from_url(url: str = Form(...)):
    """Download audio from YouTube or SoundCloud URL and extract metadata."""
    downloader_service = DownloaderService()
    audio_service = AudioService()
    
    try:
        # Download the audio
        download_result = downloader_service.download_audio(url)
        
        if not download_result["success"]:
            raise HTTPException(status_code=400, detail=download_result["error"])
        
        file_path = download_result["file_path"]
        try:
            # Extract metadata from the downloaded file
            metadata = audio_service.extract_metadata(file_path)
            
            # If title is empty, use the downloaded title
            if not metadata.title and download_result.get("original_title"):
                metadata.title = download_result["original_title"]
            
            # If artist is empty, use the uploader
            if not metadata.artist and download_result.get("uploader"):
                metadata.artist = download_result["uploader"]
            
            # Convert metadata to dict for JSON serialization
            metadata_dict = metadata.model_dump() if hasattr(metadata, 'model_dump') else metadata.dict()
            
            # Create a filename based on the title
            original_filename = f"{download_result['title']}.mp3"
            
            # Store the file in a downloads directory instead of deleting immediately
            downloads_dir = "/tmp/downloaded_audio_files"
            os.makedirs(downloads_dir, exist_ok=True)
            
            # Create a unique filename with timestamp
            timestamp = int(time.time())
            stored_filename = f"downloaded_{timestamp}_{original_filename}"
            stored_file_path = os.path.join(downloads_dir, stored_filename)
            
            # Move the file to the downloads directory
            shutil.move(file_path, stored_file_path)
            
            return JSONResponse(content={
                "success": True,
                "files": [{
                    "success": True,
                    "filename": original_filename,
                    "stored_filename": stored_filename,
                    "stored_path": stored_file_path,
                    "metadata": metadata_dict,
                    "downloaded_from": url,
                    "duration": download_result.get("duration", 0)
                }],
                "message": "Audio downloaded and processed successfully"
            })
            
        except Exception as e:
            # Clean up the downloaded file only if there was an error
            downloader_service.cleanup_file(file_path)
            raise HTTPException(status_code=500, detail=f"Error extracting metadata: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.post("/batch-download-from-urls")
async def batch_download_from_urls(urls: List[str] = Form(...)):
    """Download multiple audio files from YouTube or SoundCloud URLs."""
    downloader_service = DownloaderService()
    audio_service = AudioService()
    results = []
    
    for url in urls:
        try:
            # Download the audio
            download_result = downloader_service.download_audio(url.strip())
            
            if not download_result["success"]:
                results.append({
                    "success": False,
                    "url": url,
                    "error": download_result["error"]
                })
                continue
            
            file_path = download_result["file_path"]
            
            try:
                # Extract metadata from the downloaded file
                metadata = audio_service.extract_metadata(file_path)
                
                # If title is empty, use the downloaded title
                if not metadata.title and download_result.get("original_title"):
                    metadata.title = download_result["original_title"]
                
                # If artist is empty, use the uploader
                if not metadata.artist and download_result.get("uploader"):
                    metadata.artist = download_result["uploader"]
                
                # Convert metadata to dict for JSON serialization
                metadata_dict = metadata.model_dump() if hasattr(metadata, 'model_dump') else metadata.dict()
                
                # Create a filename based on the title
                original_filename = f"{download_result['title']}.mp3"
                
                results.append({
                    "success": True,
                    "filename": original_filename,
                    "metadata": metadata_dict,
                    "downloaded_from": url,
                    "duration": download_result.get("duration", 0)
                })
                
            except Exception as e:
                results.append({
                    "success": False,
                    "url": url,
                    "error": f"Error extracting metadata: {str(e)}"
                })
            
            finally:
                # Clean up the downloaded file
                downloader_service.cleanup_file(file_path)
                
        except Exception as e:
            results.append({
                "success": False,
                "url": url,
                "error": f"Download failed: {str(e)}"
            })
    
    return JSONResponse(content={
        "success": True,
        "files": results,
        "message": f"Processed {len(urls)} URL(s)"
    })

@router.get("/downloaded-file/{filename}")
async def get_downloaded_file(filename: str):
    """Serve a downloaded audio file."""
    downloads_dir = "/tmp/downloaded_audio_files"
    file_path = os.path.join(downloads_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Downloaded file not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/mpeg"
    )

@router.post("/update-downloaded-tags")
async def update_downloaded_audio_tags(
    stored_filename: str = Form(...),
    metadata: str = Form(...)
):
    """Update tags for a downloaded audio file using its stored filename."""
    logger.debug(f"Updating tags for downloaded file: {stored_filename}")
    logger.debug(f"Raw metadata string: {metadata}")
    
    downloads_dir = "/tmp/downloaded_audio_files"
    file_path = os.path.join(downloads_dir, stored_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Downloaded file not found")
    
    try:
        # Parse metadata JSON
        try:
            metadata_dict = json.loads(metadata)
            logger.debug(f"Parsed metadata: {metadata_dict}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON metadata: {e}")
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
        
        logger.debug(f"Created AudioMetadata object: {audio_metadata}")
        
        # Update metadata directly on the stored file
        audio_service = AudioService()
        success = audio_service.update_metadata(file_path, audio_metadata)
        
        if success:
            # Create a directory to store updated files
            updated_files_dir = "/tmp/updated_audio_files"
            os.makedirs(updated_files_dir, exist_ok=True)
            
            # Store the updated file with a unique name
            timestamp = int(time.time())
            # Extract original filename from stored filename
            original_filename = stored_filename.split('_', 2)[-1] if '_' in stored_filename else stored_filename
            updated_filename = f"updated_{timestamp}_{original_filename}"
            updated_file_path = os.path.join(updated_files_dir, updated_filename)
            
            # Copy the updated file to the storage location
            shutil.copy2(file_path, updated_file_path)
            
            logger.info(f"Successfully updated and saved file: {updated_file_path}")
            
            return JSONResponse(content={
                "success": True,
                "message": "Tags updated successfully",
                "filename": original_filename,
                "updated_filename": updated_filename
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to update tags")
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating file: {str(e)}")

