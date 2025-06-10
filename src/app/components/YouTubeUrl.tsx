import React from 'react';
import { TextField, Button, Typography, Box, CircularProgress } from '@mui/material';
import { useAddingFile } from '../vars/addingFile';
import CustomAlert from './CustomAlert';
import { getApiUrl, API_CONFIG } from '../config/api';

export default function YouTubeUrl() {
    const [youtubeLink, setYoutubeLink] = React.useState('');
    const { isAddingFile, setIsAddingFile } = useAddingFile();

    // Alert state
    const [alertMessage, setAlertMessage] = React.useState<string>('');
    const [alertSeverity, setAlertSeverity] = React.useState<'error' | 'warning' | 'info' | 'success'>('info');
    const [showAlert, setShowAlert] = React.useState<boolean>(false);

    const handleDownload = async () => {
        if (!youtubeLink.trim()) {
            setAlertMessage('Please enter a YouTube URL');
            setAlertSeverity('warning');
            setShowAlert(true);
            return;
        }

        setIsAddingFile(true);
        try {
            const formData = new FormData();
            formData.append('url', youtubeLink);            const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.DOWNLOAD_YOUTUBE), {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('YouTube download successful:', result);

            if (result.success && result.metadata) {
                // Trigger a custom event to notify TagEditor
                window.dispatchEvent(new CustomEvent('metadataLoaded', { 
                    detail: { 
                        metadata: result.metadata,
                        filename: result.filename,
                        platform: result.platform || 'youtube',
                        originalUrl: result.original_url
                    } 
                }));
                  // Clear the input
                setYoutubeLink('');
                setAlertMessage('YouTube audio downloaded successfully!');
                setAlertSeverity('success');
                setShowAlert(true);
            } else {
                throw new Error('Download succeeded but no metadata received');
            }

        } catch (error) {
            console.error('YouTube download error:', error);
            const errorMessage = error instanceof Error ? error.message : String(error);
            setAlertMessage(`Download failed: ${errorMessage}`);
            setAlertSeverity('error');
            setShowAlert(true);
        } finally {
            setIsAddingFile(false);
        }
    };

    return (
        <Box className="flex flex-col items-center space-y-4 p-6">
            <TextField
                value={youtubeLink}
                onChange={(e) => setYoutubeLink(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                variant="outlined"
                size="medium"
                fullWidth
                disabled={isAddingFile}
                sx={{ maxWidth: '400px', py: 1 }}
            />
            <Button
                variant="contained"
                color="error"
                onClick={handleDownload}
                disabled={isAddingFile || !youtubeLink.trim()}
                sx={{ px: 3, py: 1 }}
            >
                {isAddingFile ? (
                    <>
                        <CircularProgress size={16} sx={{ mr: 1, color: 'white' }} />
                        Downloading...
                    </>
                ) : (
                    'Download & Edit'
                )}            </Button>            {showAlert && (
                <Box sx={{ mt: 2 }}>
                    <CustomAlert 
                        message={alertMessage} 
                        severity={alertSeverity}
                        onClose={() => setShowAlert(false)}
                    />
                </Box>
            )}
        </Box>
    );
}