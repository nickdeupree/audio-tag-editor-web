import React from 'react';
import { Button } from '@mui/material';
import { SIZES } from '../constants/sizes';
import { useFiles } from '../vars/files';
import { useCurrentFileIndex } from '../vars/currentFileIndex';
import { useAllFilesMetadata } from '../vars/allFilesMetadata';

interface DownloadButtonsProps {
    updatedFilename?: string | null;
    metadata?: { title?: string; artist?: string; album?: string; };
    hasUnsavedChanges?: boolean;
}

export default function DownloadButtons({ updatedFilename, metadata, hasUnsavedChanges = false }: DownloadButtonsProps) {
    const { files } = useFiles();
    const { currentIndex } = useCurrentFileIndex();
    const { allFilesMetadata } = useAllFilesMetadata();
    
    // Check if there are any files uploaded
    const hasFiles = files && files.length > 0;
    const hasMultipleFiles = files && files.length > 1;      const handleDownload = async () => {
        if (!hasFiles) {
            alert('Please upload a file first');
            return;
        }
        
        if (hasUnsavedChanges) {
            alert('Please save your changes before downloading');
            return;
        }
        
        try {
            let downloadUrl;
            
            // For multiple files, get the updatedFilename for the current file
            if (hasMultipleFiles && allFilesMetadata.length > 0) {
                const currentFileData = allFilesMetadata[currentIndex];
                if (currentFileData?.updatedFilename) {
                    downloadUrl = `http://localhost:8000/upload/download/${currentFileData.updatedFilename}`;
                } else {
                    alert('Please save the current file first before downloading');
                    return;
                }
            } else {
                // For single file, use the provided updatedFilename or fallback
                if (updatedFilename) {
                    downloadUrl = `http://localhost:8000/upload/download/${updatedFilename}`;
                } else {
                    downloadUrl = 'http://localhost:8000/upload/download-latest';
                }
            }
            
            const response = await fetch(downloadUrl);
            
            if (!response.ok) {
                throw new Error(`Download failed: ${response.status} ${response.statusText}`);
            }
            
            // Use the title from metadata as the filename, with fallbacks
            let filename = 'audio_file';
            
            if (metadata?.title && metadata.title.trim()) {
                // Use the title, but sanitize it for filesystem
                filename = metadata.title.trim()
                    .replace(/[<>:"/\\|?*]/g, '') // Remove invalid filename characters
                    .replace(/\s+/g, ' ') // Normalize whitespace
                    .substring(0, 100); // Limit length
            } else if (files && files[0]) {
                // Fallback to original filename without extension
                const originalName = files[0].name;
                const lastDotIndex = originalName.lastIndexOf('.');
                filename = lastDotIndex > 0 ? originalName.substring(0, lastDotIndex) : originalName;
            }
            
            // Add .mp3 extension
            filename += '.mp3';
            
            // Create blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
        } catch (error) {
            console.error('Download error:', error);
            alert(`Download failed: ${error}`);
        }
    };    const handleDownloadAll = async () => {
        if (!hasFiles) {
            alert('Please upload files first');
            return;
        }
        
        if (hasUnsavedChanges) {
            alert('Please save your changes before downloading');
            return;
        }
        
        try {
            const response = await fetch('http://localhost:8000/upload/download-all');
            
            if (!response.ok) {
                throw new Error(`Download failed: ${response.status} ${response.statusText}`);
            }
            
            // Create blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'updated_audio_files.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
        } catch (error) {
            console.error('Download all error:', error);
            alert(`Download all failed: ${error}`);
        }
    };    return (
        <div className="flex flex-row justify-center mt-6 gap-4">            <Button 
                variant="contained" 
                size="large" 
                onClick={handleDownload}
                disabled={!hasFiles || hasUnsavedChanges}
                sx={{ 
                    width: `${SIZES.buttonSize[0]}rem`, 
                    height: `${SIZES.buttonSize[1]}rem`,
                    opacity: (!hasFiles || hasUnsavedChanges) ? 0.5 : 1
                }}
            >
                {hasMultipleFiles ? 'Download Current' : 'Download'}
            </Button>
            {hasMultipleFiles && (
                <Button 
                    variant="contained" 
                    size="medium" 
                    onClick={handleDownloadAll}
                    disabled={!hasFiles || hasUnsavedChanges}
                    sx={{ 
                        width: `${SIZES.buttonSize[0]}rem`, 
                        height: `${SIZES.buttonSize[1]}rem`,
                        opacity: (!hasFiles || hasUnsavedChanges) ? 0.5 : 1
                    }}
                >
                    Download All
                </Button>
            )}
        </div>
    );
}