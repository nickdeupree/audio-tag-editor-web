"""
Service layer for handling file operations.
"""

from fastapi import UploadFile, HTTPException
from typing import List
from models.responses import FileInfo

class FileService:
    """Service for handling file operations."""
    
    @staticmethod
    async def process_uploaded_files(files: List[UploadFile]) -> List[FileInfo]:
        """
        Process uploaded files and return file information.
        
        Args:
            files: List of uploaded files
            
        Returns:
            List of FileInfo objects containing file metadata
        """
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        file_info = []
        
        print(f"\n🎵 Received {len(files)} file(s):")
        print("-" * 50)
        
        for file in files:
            try:
                # Read file to get size
                content = await file.read()
                file_size = len(content)
                
                # Print file information
                print(f"📁 File: {file.filename}")
                print(f"   Type: {file.content_type}")
                print(f"   Size: {file_size} bytes")
                print()
                
                # Reset file position after reading
                await file.seek(0)
                
                file_info.append(FileInfo(
                    filename=file.filename or "unknown",
                    content_type=file.content_type or "unknown",
                    size=file_size
                ))
                
            except Exception as e:
                print(f"Error processing file {file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error processing file {file.filename}: {str(e)}"
                )
        
        print("-" * 50)
        print("All files processed successfully!\n")
        
        return file_info
