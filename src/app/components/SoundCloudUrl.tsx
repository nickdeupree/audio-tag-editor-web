import React from 'react';
import { TextField, Button, Typography, Box, CircularProgress } from '@mui/material';

export default function SoundCloudUrl() {
    const [soundcloudLink, setSoundcloudLink] = React.useState('');
    const [isDownloading, setIsDownloading] = React.useState(false);

    const handleDownload = async () => {
        if (!soundcloudLink.trim()) {
            alert('Please enter a SoundCloud URL');
            return;
        }

        setIsDownloading(true);
        try {
            const formData = new FormData();
            formData.append('url', soundcloudLink);

            const response = await fetch('http://localhost:8000/upload/download/soundcloud', {
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
                alert('SoundCloud audio downloaded successfully!');
            } else {
                throw new Error('Download succeeded but no metadata received');
            }

        } catch (error) {
            console.error('SoundCloud download error:', error);
            const errorMessage = (error instanceof Error) ? error.message : String(error);
            alert(`Download failed: ${errorMessage}`);
        } finally {
            setIsDownloading(false);
        }
    };

    return (
        <Box className="flex flex-col items-center space-y-4 p-6">
            <Typography variant="h6" component="label" style={{ color: 'var(--color-text)' }}>
                SoundCloud URL
            </Typography>
            <TextField
                value={soundcloudLink}
                onChange={(e) => setSoundcloudLink(e.target.value)}
                placeholder="https://soundcloud.com/..."
                variant="outlined"
                size="medium"
                fullWidth
                disabled={isDownloading}
                sx={{ maxWidth: '400px', py: 1 }}
            />
            <Button
                variant="contained"
                onClick={handleDownload}
                disabled={isDownloading || !soundcloudLink.trim()}
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
                {isDownloading ? (
                    <>
                        <CircularProgress size={16} sx={{ mr: 1, color: 'white' }} />
                        Downloading...
                    </>
                ) : (
                    'Download & Edit'
                )}
            </Button>
        </Box>
    );
}