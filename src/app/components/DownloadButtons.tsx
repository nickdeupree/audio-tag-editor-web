import React from 'react';
import { Button } from '@mui/material';
import { SIZES } from '../constants/sizes';
import { getApiUrl, API_CONFIG } from '../config/api';

interface DownloadButtonsProps {
    currentFilename?: string;
    metadata?: { title?: string; artist?: string; album?: string; };
    isSaving?: boolean;
    lastSaveTime?: Date | null;
    hasPendingChanges?: boolean;
}

export default function DownloadButtons({ currentFilename, metadata, isSaving, lastSaveTime, hasPendingChanges }: DownloadButtonsProps) {
    // Alert state
    const [alertMessage, setAlertMessage] = React.useState<string>('');
    const [alertSeverity, setAlertSeverity] = React.useState<'error' | 'warning' | 'info' | 'success'>('info');
    const [showAlert, setShowAlert] = React.useState<boolean>(false);
    
    const handleDownload = async () => {
        // Prevent download while saving or if there are pending changes
        if (isSaving || hasPendingChanges) {
            const message = isSaving 
                ? 'Please wait for the file to finish saving before downloading.'
                : 'You have unsaved changes. Please wait for auto-save to complete.';
            setAlertMessage(message);
            setAlertSeverity('warning');
            setShowAlert(true);
            return;
        }

        try {
            // Debug: Check what files are available and validate filename
            console.log('Current filename for download:', currentFilename);
            
            if (!currentFilename) {
                setAlertMessage('No file selected for download');
                setAlertSeverity('error');
                setShowAlert(true);
                return;
            }

            // Encode the filename for URL safety
            const encodedFilename = encodeURIComponent(currentFilename);
            const downloadUrl = `${getApiUrl(API_CONFIG.ENDPOINTS.DOWNLOAD_BY_FILENAME)}/${encodedFilename}`;
            console.log('Download URL:', downloadUrl);
            
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
        // Prevent download while saving or if there are pending changes
        if (isSaving || hasPendingChanges) {
            const message = isSaving 
                ? 'Please wait for the file to finish saving before downloading.'
                : 'You have unsaved changes. Please wait for auto-save to complete.';
            setAlertMessage(message);
            setAlertSeverity('warning');
            setShowAlert(true);
            return;
        }

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
            <div className="flex flex-row justify-center mt-6 gap-4">
                <Button 
                    variant="contained" 
                    size="large" 
                    onClick={handleDownload}
                    disabled={isSaving || hasPendingChanges}
                    sx={{ 
                        width: `${SIZES.buttonSize[0]}rem`, 
                        height: `${SIZES.buttonSize[1]}rem`,
                        opacity: (isSaving || hasPendingChanges) ? 0.6 : 1
                    }}
                >
                    {(isSaving || hasPendingChanges) ? 'Saving...' : 'Download'}
                </Button>
                <Button 
                    variant="contained" 
                    size="medium" 
                    onClick={handleDownloadAll}
                    disabled={isSaving || hasPendingChanges}
                    sx={{ 
                        width: `${SIZES.buttonSize[0]}rem`, 
                        height: `${SIZES.buttonSize[1]}rem`,
                        opacity: (isSaving || hasPendingChanges) ? 0.6 : 1
                    }}
                >
                    {(isSaving || hasPendingChanges) ? 'Saving...' : 'Download All'}
                </Button>
            </div>
    );
}