import React from 'react';
import { Box, Button } from '@mui/material';
import { SIZES } from '../constants/sizes';
import CustomAlert from './CustomAlert';
import { getApiUrl, API_CONFIG } from '../config/api';

interface DownloadButtonsProps {
    currentIndex?: number;
    metadata?: { title?: string; artist?: string; album?: string; };
}

export default function DownloadButtons({ currentIndex, metadata }: DownloadButtonsProps) {
    // Alert state
    const [alertMessage, setAlertMessage] = React.useState<string>('');
    const [alertSeverity, setAlertSeverity] = React.useState<'error' | 'warning' | 'info' | 'success'>('info');
    const [showAlert, setShowAlert] = React.useState<boolean>(false);
    
    const handleDownload = async () => {
        try {
            // Debug: Check what files are available
            console.log('Current index for download:', currentIndex);
            try {
                const filesResponse = await fetch(`${getApiUrl(API_CONFIG.ENDPOINTS.DOWNLOAD_BY_INDEX).replace('/download', '/files/all')}`);
                if (filesResponse.ok) {
                    const filesData = await filesResponse.json();
                    console.log('Available files:', filesData);
                    console.log('Total files:', filesData?.files?.length || 0);
                    
                    // Check if the requested index exists
                    if (currentIndex !== undefined && currentIndex >= filesData?.files?.length) {
                        throw new Error(`File index ${currentIndex} not found. Only ${filesData?.files?.length} files available.`);
                    }
                } else {
                    console.warn('Could not fetch files list:', filesResponse.status);
                }
            } catch (debugError) {
                console.warn('Debug files fetch error:', debugError);
            }
            
            let downloadUrl;
            if (currentIndex !== undefined && currentIndex >= 0) {
                // Download specific file by index using direct backend call
                downloadUrl = `${getApiUrl(API_CONFIG.ENDPOINTS.DOWNLOAD_BY_INDEX)}/${currentIndex}`;
                console.log('Download URL:', downloadUrl);
            } else {
                // Fallback to latest file
                downloadUrl = getApiUrl(API_CONFIG.ENDPOINTS.DOWNLOAD_LATEST);
                console.log('Fallback download URL:', downloadUrl);
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
            setAlertMessage(`Download failed: ${error}`);
            setAlertSeverity('error');
            setShowAlert(true);
        }
    };
    
    const handleDownloadAll = async () => {
        try {
            const downloadUrl = getApiUrl(API_CONFIG.ENDPOINTS.DOWNLOAD_ALL);
            
            const response = await fetch(downloadUrl);
            
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
            setAlertMessage(`Download all failed: ${error}`);
            setAlertSeverity('error');
            setShowAlert(true);
        }
    };      return (
        <>
            <div className="flex flex-row justify-center mt-6 gap-4">
                <Button 
                    variant="contained" 
                    size="large" 
                    onClick={handleDownload}
                    sx={{ width: `${SIZES.buttonSize[0]}rem`, height: `${SIZES.buttonSize[1]}rem` }}
                >
                    Download
                </Button>
                <Button 
                    variant="contained" 
                    size="medium" 
                    onClick={handleDownloadAll}
                    sx={{ width: `${SIZES.buttonSize[0]}rem`, height: `${SIZES.buttonSize[1]}rem` }}
                >
                    Download All
                </Button>
            </div>            {showAlert && (
                <Box sx={{ mt: 2 }}>
                    <CustomAlert 
                        message={alertMessage} 
                        severity={alertSeverity}
                        onClose={() => setShowAlert(false)}
                    />
                </Box>
            )}
        </>
    );
}