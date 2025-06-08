import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { SIZES } from '../constants/sizes';
import { useFiles } from '../vars/files';

interface DownloadButtonsProps {
    updatedFilename?: string | null;
    metadata?: { title?: string; artist?: string; album?: string; };
}

export default function DownloadButtons({ updatedFilename, metadata }: DownloadButtonsProps) {
    const { files } = useFiles();
    const handleDownload = async () => {
        try {
            let downloadUrl;
            if (updatedFilename) {
                // Download specific updated file
                downloadUrl = `http://localhost:8000/upload/download/${updatedFilename}`;
            } else {
                // Fallback to latest updated file
                downloadUrl = 'http://localhost:8000/upload/download-latest';
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
    };
    
    return (
        <div className="flex flex-row justify-center mt-6 gap-4">
            <Button 
                variant="contained" 
                size="large" 
                onClick={handleDownload}
                sx={{ width: `${SIZES.buttonSize[0]}rem`, height: `${SIZES.buttonSize[1]}rem` }}
            >
                Download
            </Button>
            <Button variant="contained" size="medium" sx={{ width: `${SIZES.buttonSize[0]}rem`, height: `${SIZES.buttonSize[1]}rem` }}>
                Upload to YTM
            </Button>
        </div>
    );
}