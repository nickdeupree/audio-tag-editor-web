import React from 'react';
import { TextField, Button, Box, CircularProgress } from '@mui/material';
import { useAddingFile } from '../vars/addingFile';
import CustomAlert from './CustomAlert';
import { getApiUrl, API_CONFIG } from '../config/api';

export default function SoundCloudUrl() {
    const [soundcloudLink, setSoundcloudLink] = React.useState('');
    const { isAddingFile, setIsAddingFile } = useAddingFile();

    // Alert state
    const [alertMessage, setAlertMessage] = React.useState<string>('');
    const [alertSeverity, setAlertSeverity] = React.useState<'error' | 'warning' | 'info' | 'success'>('info');
    const [showAlert, setShowAlert] = React.useState<boolean>(false);

    const handleDownload = async () => {
        if (!soundcloudLink.trim()) {
            setAlertMessage('Please enter a SoundCloud URL');
            setAlertSeverity('warning');
            setShowAlert(true);
            return;
        }

        setIsAddingFile(true);
        try {
            const formData = new FormData();
            formData.append('url', soundcloudLink);            const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.DOWNLOAD_SOUNDCLOUD), {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('SoundCloud download successful:', result);

            if (result.success && result.metadata) {
                // Trigger a custom event to notify TagEditor
                window.dispatchEvent(new CustomEvent('metadataLoaded', { 
                    detail: { 
                        metadata: result.metadata,
                        filename: result.filename,
                        platform: result.platform || 'soundcloud',
                        originalUrl: result.original_url
                    } 
                }));
                  // Clear the input
                setSoundcloudLink('');
                setAlertMessage('SoundCloud audio downloaded successfully!');
                setAlertSeverity('success');
                setShowAlert(true);
            } else {
                throw new Error('Download succeeded but no metadata received');
            }

        } catch (error) {
            console.error('SoundCloud download error:', error);
            const errorMessage = (error instanceof Error) ? error.message : String(error);
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
                value={soundcloudLink}
                onChange={(e) => setSoundcloudLink(e.target.value)}
                placeholder="https://soundcloud.com/..."
                variant="outlined"
                size="medium"
                fullWidth
                disabled={isAddingFile}
                sx={{ maxWidth: '400px', py: 1 }}
            />
            <Button
                variant="contained"
                onClick={handleDownload}
                disabled={isAddingFile || !soundcloudLink.trim()}
                sx={{ 
                    px: 3, 
                    py: 1,
                    backgroundColor: '#ff5500',
                    '&:hover': {
                        backgroundColor: '#e64900'
                    },
                    '&:disabled': {
                        backgroundColor: '#cccccc'
                    }
                }}
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