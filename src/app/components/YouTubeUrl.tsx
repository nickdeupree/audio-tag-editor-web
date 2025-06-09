import React from 'react';
import { TextField, Button, Typography, Box, CircularProgress } from '@mui/material';

export default function YouTubeUrl() {
    const [youtubeLink, setYoutubeLink] = React.useState('');
    const [isDownloading, setIsDownloading] = React.useState(false);

    const handleDownload = async () => {
        if (!youtubeLink.trim()) {
            alert('Please enter a YouTube URL');
            return;
        }

        setIsDownloading(true);
        try {
            const formData = new FormData();
            formData.append('url', youtubeLink);

            const response = await fetch('http://localhost:8000/upload/download/youtube', {
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
                alert('YouTube audio downloaded successfully!');
            } else {
                throw new Error('Download succeeded but no metadata received');
            }

        } catch (error) {
            console.error('YouTube download error:', error);
            const errorMessage = error instanceof Error ? error.message : String(error);
            alert(`Download failed: ${errorMessage}`);
        } finally {
            setIsDownloading(false);
        }
    };

    return (
        <Box className="flex flex-col items-center space-y-4 p-6">
            <Typography variant="h6" component="label" style={{ color: 'var(--color-text)' }}>
                YouTube URL
            </Typography>
            <TextField
                value={youtubeLink}
                onChange={(e) => setYoutubeLink(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                variant="outlined"
                size="medium"
                fullWidth
                disabled={isDownloading}
                sx={{ maxWidth: '400px', py: 1 }}
            />
            <Button
                variant="contained"
                color="error"
                onClick={handleDownload}
                disabled={isDownloading || !youtubeLink.trim()}
                sx={{ px: 3, py: 1 }}
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