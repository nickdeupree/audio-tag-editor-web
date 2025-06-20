"""
Upload router for handling file uploads and audio tag operations.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from services.unified_file_service import UnifiedFileService
from services.tag_update_service import TagUpdateService
from services.downloader_service import DownloadService
from models.responses import AudioUploadResponse
from utils.debug import debug
from typing import List
import os
import logging

router = APIRouter(prefix="/upload")
debug.enable()

# Initialize services
unified_file_service = UnifiedFileService()
tag_update_service = TagUpdateService()
download_service = DownloadService()

# Configure logging
logger = logging.getLogger(__name__)

@router.post("/clear-cache")
async def clear_download_cache():
    """Clear the workspace to start fresh."""
    result = unified_file_service.clear_workspace()
    return {
        "success": True,
        "message": f"Cleared workspace: {result['message']}",
        "files_cleaned": result['files_count']
    }

@router.post("/", response_model=AudioUploadResponse)
async def upload_audio_file(files: List[UploadFile] = File(...)):
    """Upload audio files and add them to the workspace."""
    return await unified_file_service.add_uploaded_files(files)

@router.post("/add/youtube")
async def add_youtube_audio(url: str = Form(...)):
    """Download YouTube audio and add to workspace."""
    return await unified_file_service.add_youtube_audio(url)

@router.post("/add/soundcloud")
async def add_soundcloud_audio(url: str = Form(...)):
    """Download SoundCloud audio and add to workspace."""
    return await unified_file_service.add_soundcloud_audio(url)

@router.post("/update-tags")
async def update_audio_tags(
    file: UploadFile = File(...), 
    metadata: str = Form(...)
):
    """Update audio file tags with new metadata."""
    logger.debug(f"update_audio_tags called. Uploaded filename: {file.filename}")
    logger.debug(f"Received metadata for update: {metadata}")
    try:
        result = await tag_update_service.update_file_tags(file, metadata)
        logger.debug(f"Tag update result: {result}")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in update_audio_tags for file {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating file tags: {str(e)}")

@router.post("/update-tags-workspace/{stored_filename}")
async def update_tags_workspace(
    stored_filename: str,
    metadata: str = Form(...)
):
    """Update tags for a file already in the workspace."""
    logger.info(f"API called to update tags for: {stored_filename}")
    logger.debug(f"update_tags_workspace called with stored_filename: {stored_filename}")
    logger.debug(f"Received metadata for workspace update: {metadata}")
    try:
        metadata_obj = tag_update_service.parse_metadata_from_form(metadata)
        logger.debug(f"Parsed metadata_obj: {metadata_obj}")
        updated_filename = unified_file_service.update_file_metadata(stored_filename, metadata_obj)
        
        logger.debug(f"File metadata updated. New filename: {updated_filename}")
        return JSONResponse(content={
            "success": True,
            "message": "Tags updated successfully",
            "original_filename": stored_filename,
            "updated_filename": updated_filename
        })
        
    except Exception as e:
        logger.error(f"Error updating tags for {stored_filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating file tags: {str(e)}")

@router.post("/cover-art")
async def update_cover_art(
    audio_file: UploadFile = File(...),
    cover_file: UploadFile = File(...)
):
    """Update cover art for an audio file."""
    result = await tag_update_service.update_cover_art(audio_file, cover_file)
    return JSONResponse(content=result)

@router.get("/files/all")
async def get_all_files():
    """Get all files in the workspace."""
    return unified_file_service.get_all_files()

@router.get("/download/by-filename/{filename}")
async def download_file_by_filename(filename: str):
    """Download a specific file by its original filename."""
    file_info = unified_file_service.get_file_by_filename(unified_file_service._extract_original_filename(filename))
    
    if not file_info:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
    
    file_path = file_info['full_path']
    original_filename = file_info['filename']
    debug.print(f"file_path: {file_path}")
    debug.print(f"original_filename: {original_filename}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type='application/octet-stream'
    )

@router.get("/download-latest")
async def download_latest_file():
    """Download the most recently added file."""
    # Get the first file (index 0) which is the most recent
    file_info = unified_file_service.get_file_by_index(0)
    
    if not file_info:
        raise HTTPException(status_code=404, detail="No files available for download")
    
    file_path = file_info['full_path']
    original_filename = file_info['filename']
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type='application/octet-stream'
    )

@router.get("/download-all")
async def download_all_files():
    """Download all files as a zip archive."""
    zip_path = unified_file_service.create_download_archive()
    
    return FileResponse(
        path=zip_path,
        filename="audio_workspace.zip",
        media_type='application/zip'
    )

@router.post("/download-selected")
async def download_selected_files(indices: List[int]):
    """Download selected files by their indices as a zip archive."""
    zip_path = unified_file_service.create_download_archive(indices)
    
    return FileResponse(
        path=zip_path,
        filename="selected_audio_files.zip",
        media_type='application/zip'
    )

@router.get("/debug/workspace")
async def debug_workspace():
    """Get debug information about the workspace."""
    return unified_file_service.get_workspace_debug_info()

@router.get("/debug/status")
async def get_debug_status():
    """Get current debug mode status."""
    return JSONResponse(content={
        "debug_enabled": debug.is_enabled(),
        "message": f"Debug mode is {'enabled' if debug.is_enabled() else 'disabled'}"
    })

@router.post("/debug/toggle")
async def toggle_debug_mode():
    """Toggle debug mode on/off."""
    new_state = debug.toggle()
    return JSONResponse(content={
        "debug_enabled": new_state,
        "message": f"Debug mode {'enabled' if new_state else 'disabled'}"
    })

@router.post("/debug/enable")
async def enable_debug_mode():
    """Enable debug mode."""
    debug.enable()
    return JSONResponse(content={
        "debug_enabled": True,
        "message": "Debug mode enabled"
    })

@router.post("/debug/disable")
async def disable_debug_mode():
    """Disable debug mode."""
    debug.disable()
    return JSONResponse(content={
        "debug_enabled": False,
        "message": "Debug mode disabled"
    })

@router.get("/test-download")
async def test_download_service():
    """Test the download service functionality."""
    try:
        test_result = download_service.test_ytdl_functionality()
        
        return JSONResponse(content={
            "success": test_result['success'],
            "message": "Download service test completed",
            "test_result": test_result
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Download service test failed: {str(e)}"
            }
        )

# Legacy endpoints for backward compatibility
@router.post("/download/youtube")
async def download_youtube_audio(url: str = Form(...)):
    """Legacy endpoint - use /add/youtube instead."""
    return await add_youtube_audio(url)

@router.post("/download/soundcloud")
async def download_soundcloud_audio(url: str = Form(...)):
    """Legacy endpoint - use /add/soundcloud instead."""
    return await add_soundcloud_audio(url)

@router.get("/download/{stored_filename}")
async def download_file_by_stored_filename(stored_filename: str):
    """Download a file by its stored filename."""
    logger.info(f"File downloaded: {stored_filename}")
    file_path = unified_file_service.get_file_by_stored_filename(stored_filename)
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {stored_filename}")
    
    # Extract original filename
    original_filename = unified_file_service._extract_original_filename(stored_filename)
    
    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type='application/octet-stream'
    )
