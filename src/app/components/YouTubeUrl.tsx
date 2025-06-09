import React, { useState } from 'react';
import { TextField, Button, Typography, Box, CircularProgress } from '@mui/material';
import { useFiles } from '../vars/files';
import { useAllFilesMetadata } from '../vars/allFilesMetadata';
import { useNumFiles } from '../vars/numFiles';
import { useCurrentFileIndex } from '../vars/currentFileIndex';

export default function YouTubeUrl() {
    const [youtubeLink, setYoutubeLink] = useState('');
    const [isDownloading, setIsDownloading] = useState(false);
    const { files, setFiles } = useFiles();
    const { allFilesMetadata, setAllFilesMetadata } = useAllFilesMetadata();
    const { setNumFiles } = useNumFiles();
    const { setCurrentIndex } = useCurrentFileIndex();

    const handleDownload = async () => {
        if (!youtubeLink.trim()) {
            alert('Please enter a YouTube URL');
            return;
        }

        setIsDownloading(true);
        try {
            const formData = new FormData();
            formData.append('url', youtubeLink.trim());

            const response = await fetch('http://localhost:8000/upload/download-from-url', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Download failed');
            }

            const result = await response.json();
            
            if (result.success && result.files && result.files.length > 0) {
                const downloadedFile = result.files[0];
                
                if (downloadedFile.success) {
                    // Create a dummy File object for the downloaded audio
                    const dummyFile = new File([''], downloadedFile.filename, { 
                        type: 'audio/mpeg' 
                    });
                    
                    // Add to files array
                    const newFiles = files ? [...files, dummyFile] : [dummyFile];
                    
                    // Convert File array to FileList
                    const dataTransfer = new DataTransfer();
                    newFiles.forEach(file => dataTransfer.items.add(file));
                    setFiles(dataTransfer.files);
                      // Add to metadata array
                    const newMetadataEntry = {
                        filename: downloadedFile.filename,
                        metadata: downloadedFile.metadata,
                        downloadedFrom: downloadedFile.downloaded_from,
                        isDownloaded: true,
                        storedFilename: downloadedFile.stored_filename
                    };
                    
                    const newAllMetadata = [...allFilesMetadata, newMetadataEntry];
                    setAllFilesMetadata(newAllMetadata);
                    
                    // Update counts and navigation
                    setNumFiles(newFiles.length);
                    setCurrentIndex(newFiles.length - 1); // Navigate to the new file
                    
                    // Clear the input
                    setYoutubeLink('');
                    
                    // Dispatch metadata loaded event for the TagEditor
                    const event = new CustomEvent('metadataLoaded', {
                        detail: {
                            metadata: downloadedFile.metadata,
                            filename: downloadedFile.filename,
                            fileIndex: newFiles.length - 1
                        }
                    });
                    window.dispatchEvent(event);
                    
                    alert('YouTube audio downloaded successfully!');
                } else {
                    throw new Error(downloadedFile.error || 'Download failed');
                }
            } else {
                throw new Error('No valid files were downloaded');
            }
            
        } catch (error) {
            console.error('Download error:', error);
            alert(`Download failed: ${error}`);
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
                sx={{ px: 3, py: 1, minWidth: '160px' }}
            >
                {isDownloading ? (
                    <>
                        <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
                        Downloading...
                    </>
                ) : (
                    'Download & Edit'
                )}
            </Button>
        </Box>
    );
}