import React, { useState, useEffect } from 'react';
import { Box, Button, TextField, Pagination, Typography } from '@mui/material';
import UploadIcon from '@mui/icons-material/Upload';
import DownloadButtons from './DownloadButtons';
import { SIZES } from '../constants/sizes';
import { useBatch } from '../vars/isBatch';
import { useNumFiles } from '../vars/numFiles';
import { useFiles } from '../vars/files';

interface AudioMetadata {
    title?: string;
    artist?: string;
    album?: string;
    genre?: string;
    year?: number;
    track?: string;
    duration?: number;
    cover_art?: string;  // Base64 encoded cover art
    cover_art_mime_type?: string;  // MIME type of the cover art
}

export default function TagEditor() {
    const { isBatch } = useBatch();
    const { numFiles } = useNumFiles();
    const { files } = useFiles();
    
    // State for form fields
    const [metadata, setMetadata] = useState<AudioMetadata>({
        title: '',
        artist: '',
        album: '',
        genre: '',
    });
    const [currentFilename, setCurrentFilename] = useState<string>('');
    const [updatedFilename, setUpdatedFilename] = useState<string | null>(null);
    const [coverArtUrl, setCoverArtUrl] = useState<string | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [platform, setPlatform] = useState<string | null>(null);
    const [originalUrl, setOriginalUrl] = useState<string | null>(null);

    // Load metadata when component mounts or when new metadata is available
    useEffect(() => {
        // Listen for metadata loaded events
        const handleMetadataLoaded = (event: CustomEvent) => {
            const { metadata: newMetadata, filename, platform: filePlatform, originalUrl: fileOriginalUrl } = event.detail;
            setMetadata({
                title: newMetadata.title || '',
                artist: newMetadata.artist || '',
                album: newMetadata.album || '',
                genre: newMetadata.genre || '',
                year: newMetadata.year || undefined,
                cover_art: newMetadata.cover_art || undefined,
                cover_art_mime_type: newMetadata.cover_art_mime_type || undefined,
            });
            setCurrentFilename(filename);
            setPlatform(filePlatform || null);
            setOriginalUrl(fileOriginalUrl || null);
            
            // Set cover art URL if available
            if (newMetadata.cover_art && newMetadata.cover_art_mime_type) {
                setCoverArtUrl(`data:${newMetadata.cover_art_mime_type};base64,${newMetadata.cover_art}`);
            } else {
                setCoverArtUrl(null);
            }
        };

        window.addEventListener('metadataLoaded', handleMetadataLoaded as EventListener);

        return () => {
            window.removeEventListener('metadataLoaded', handleMetadataLoaded as EventListener);
        };
    }, []);

    // Handle input changes
    const handleInputChange = (field: keyof AudioMetadata) => (event: React.ChangeEvent<HTMLInputElement>) => {
        setMetadata(prev => ({
            ...prev,
            [field]: event.target.value
        }));
    };

    // Handle cover art upload
    const handleCoverArtUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
                return;
            }

            // Create a canvas to resize the image
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                const maxSize = 500;
                let { width, height } = img;
                
                // Calculate new dimensions maintaining aspect ratio
                if (width > height) {
                    if (width > maxSize) {
                        height = (height * maxSize) / width;
                        width = maxSize;
                    }
                } else {
                    if (height > maxSize) {
                        width = (width * maxSize) / height;
                        height = maxSize;
                    }
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // Draw and compress the image
                ctx?.drawImage(img, 0, 0, width, height);
                
                // Convert to blob with compression
                canvas.toBlob((blob) => {
                    if (blob) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            const result = e.target?.result as string;
                            if (result) {
                                // Extract base64 data
                                const base64Data = result.split(',')[1];
                                
                                setMetadata(prev => ({
                                    ...prev,
                                    cover_art: base64Data,
                                    cover_art_mime_type: file.type
                                }));
                                
                                setCoverArtUrl(result);
                            }
                        };
                        reader.readAsDataURL(blob);
                    }
                }, file.type, 0.8); // 0.8 = 80% quality for JPEG compression
            };
            
            const reader = new FileReader();
            reader.onload = (e) => {
                if (e.target?.result) {
                    img.src = e.target.result as string;
                }
            };
            reader.readAsDataURL(file);
        }
    };

    // Handle save button click
    const handleSave = async () => {
        console.log('Metadata saved:', metadata);
        const currentFile = files && files.length > 0 ? files[0] : null;
        if(!currentFile){
            alert('No file selected to save');
            return;
        }
        setIsSaving(true);
        try{
            const formData = new FormData();
            formData.append('file', currentFile);
            
            // Clean up the metadata object - remove undefined values and handle nulls properly
            const metadataToSend = {
                title: metadata.title || null,
                artist: metadata.artist || null,
                album: metadata.album || null,
                genre: metadata.genre || null,
                year: metadata.year || null,
                cover_art: metadata.cover_art || null,
                cover_art_mime_type: metadata.cover_art_mime_type || null,
            };
            
            console.log('Sending metadata:', metadataToSend);
            formData.append('metadata', JSON.stringify(metadataToSend));
            
            const response = await fetch('http://localhost:8000/upload/update-tags', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                // Try to get more detailed error information
                let errorMessage = `Error: ${response.status} ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch {
                    // If we can't parse the error response, use the status text
                }
                throw new Error(errorMessage);
            }
            
            const result = await response.json();

            if (result.success){
                alert('Metadata saved successfully');
                // Store the updated filename for download
                if (result.updated_filename) {
                    setUpdatedFilename(result.updated_filename);
                }
            }else{
                throw new Error(result.message || 'Failed to update tags');
            }
        } catch(error){
            console.error('Error saving metadata:', error);
            alert(`Error saving metadata: ${error}`);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="flex flex-col">
            <div className="w-full h-full flex flex-row items-start justify-center gap-6">
                <div className="flex flex-col">
                    <div
                        style={{
                            width: `${SIZES.artSize}rem`,
                            height: `${SIZES.artSize}rem`,
                            border: '2px solid #ccc',
                            borderRadius: 0,
                            overflow: 'hidden',
                            cursor: 'pointer',
                            position: 'relative',
                            backgroundImage: coverArtUrl ? `url(${coverArtUrl})` : 'none',
                            backgroundSize: 'cover',
                            backgroundPosition: 'center',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundColor: coverArtUrl ? 'transparent' : '#f5f5f5'
                        }}
                        onClick={() => document.getElementById('cover-art-input')?.click()}
                    >
                        {!coverArtUrl && <UploadIcon sx={{ fontSize: 48, color: '#999' }} />}
                        <input
                            id="cover-art-input"
                            type="file"
                            accept="image/*"
                            style={{ display: 'none' }}
                            onChange={handleCoverArtUpload}
                        />
                    </div>
                    {coverArtUrl && (
                        <Button
                            size="small"
                            onClick={() => {
                                setCoverArtUrl(null);
                                setMetadata(prev => ({
                                    ...prev,
                                    cover_art: undefined,
                                    cover_art_mime_type: undefined
                                }));
                            }}
                            sx={{ mt: 1, fontSize: '0.75rem' }}
                        >
                            Remove Cover
                        </Button>
                    )}
                </div>
                <div className="flex flex-col">
                    <TextField 
                        id="title-text" 
                        variant="outlined" 
                        size="small" 
                        label="title" 
                        fullWidth 
                        value={metadata.title}
                        onChange={handleInputChange('title')}
                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />
                    <TextField 
                        id="album-text" 
                        variant="outlined" 
                        size="small" 
                        label="album" 
                        fullWidth 
                        value={metadata.album}
                        onChange={handleInputChange('album')}
                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />
                    <TextField 
                        id="artist-text" 
                        variant="outlined" 
                        size="small" 
                        label="artist" 
                        fullWidth 
                        value={metadata.artist}
                        onChange={handleInputChange('artist')}
                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />
                    <TextField 
                        id="year-text" 
                        variant="outlined" 
                        size="small" 
                        label="year" 
                        fullWidth 
                        type="number"
                        value={metadata.year || ''}
                        onChange={(e) => {
                            const value = e.target.value;
                            setMetadata(prev => ({
                                ...prev,
                                year: value ? parseInt(value) : undefined
                            }));
                        }}
                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />
                    <TextField 
                        id="genre-text" 
                        variant="outlined" 
                        size="small" 
                        label="genre" 
                        fullWidth 
                        value={metadata.genre}
                        onChange={handleInputChange('genre')}
                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />
                    <Button 
                        variant="contained" 
                        size="small" 
                        onClick={handleSave}
                        loading={isSaving}
                        disabled={isSaving || !files || files.length === 0}
                        sx={{mb: 2, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }}
                    >
                        Save
                    </Button>
                </div>
            </div>
            <div className="flex flex-col items-center justify-center">
                {isBatch ? (
                <>
                    <Typography variant="body1" sx={{ mb: 1 }}>
                        {currentFilename || 'No file selected'}
                    </Typography>
                    <Pagination count={numFiles} size="medium" showFirstButton showLastButton color="standard" />
                </>
                ) : (
                    <Box sx={{ width: 210, height: 32 }}>
                        {currentFilename && (
                            <div>
                                <Typography variant="body2" sx={{ textAlign: 'center' }}>
                                    {currentFilename}
                                </Typography>
                                {platform && platform !== 'upload' && (
                                    <Typography 
                                        variant="caption" 
                                        sx={{ 
                                            textAlign: 'center', 
                                            display: 'block',
                                            color: platform === 'youtube' ? '#FF0000' : platform === 'soundcloud' ? '#ff5500' : 'inherit',
                                            fontWeight: 'bold'
                                        }}
                                    >
                                        From {platform === 'youtube' ? 'YouTube' : platform === 'soundcloud' ? 'SoundCloud' : platform}
                                    </Typography>
                                )}
                            </div>
                        )}
                    </Box>
                )
                }
                <DownloadButtons updatedFilename={updatedFilename} metadata={metadata} />
            </div>
        </div>
    );
}
