import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Button, TextField, Pagination, Typography } from '@mui/material';
import UploadIcon from '@mui/icons-material/Upload';
import DownloadButtons from './DownloadButtons';
import CustomAlert from './CustomAlert';
import { SIZES } from '../constants/sizes';
import { useBatch } from '../vars/isBatch';
import { useNumFiles } from '../vars/numFiles';
import { useFiles } from '../vars/files';
import { useCurrentFileIndex } from '../vars/currentFileIndex';
import { useAllFilesMetadata } from '../vars/allFilesMetadata';
import { getApiUrl, API_CONFIG } from '../config/api';

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
    const { files } = useFiles();    const { currentIndex, setCurrentIndex } = useCurrentFileIndex();
    const { allFilesMetadata, setAllFilesMetadata, addFileMetadata, updateFileMetadata, setUpdatedFilename: setUpdatedFilenameInContext } = useAllFilesMetadata();
    
    // State for form fields
    const [metadata, setMetadata] = useState<AudioMetadata>({
        title: '',
        artist: '',
        album: '',
        genre: '',
    });    const [currentFilename, setCurrentFilename] = useState<string>('');
    const [updatedFilename, setUpdatedFilename] = useState<string | null>(null);
    const [coverArtUrl, setCoverArtUrl] = useState<string | null>(null);
    const [platform, setPlatform] = useState<string | null>(null);    const [originalUrl, setOriginalUrl] = useState<string | null>(null);

    // Alert state
    const [alertMessage, setAlertMessage] = useState<string>('');
    const [alertSeverity, setAlertSeverity] = useState<'error' | 'warning' | 'info' | 'success'>('info');
    const [showAlert, setShowAlert] = useState<boolean>(false);

    // Auto-save related state and refs
    const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const isAutoSavingRef = useRef<boolean>(false);

    // Get current file metadata from allFilesMetadata
    const currentFileMetadata = allFilesMetadata[currentIndex];
    const allUpdatedFilenames = allFilesMetadata
        .filter(f => f.updatedFilename)
        .map(f => f.updatedFilename!);    // Load metadata when component mounts or when allFilesMetadata changes
    useEffect(() => {
        if (allFilesMetadata.length > 0 && allFilesMetadata[currentIndex]) {
            const currentFile = allFilesMetadata[currentIndex];
            
            setMetadata({
                title: currentFile.metadata.title || '',
                artist: currentFile.metadata.artist || '',
                album: currentFile.metadata.album || '',
                genre: currentFile.metadata.genre || '',
                year: currentFile.metadata.year || undefined,
                cover_art: currentFile.metadata.cover_art || undefined,
                cover_art_mime_type: currentFile.metadata.cover_art_mime_type || undefined,
            });
            setCurrentFilename(currentFile.filename);
            
            if (currentFile.metadata.cover_art && currentFile.metadata.cover_art_mime_type) {
                setCoverArtUrl(`data:${currentFile.metadata.cover_art_mime_type};base64,${currentFile.metadata.cover_art}`);
            } else {
                setCoverArtUrl(null);
            }
        }
    }, [allFilesMetadata, currentIndex]);

    // Update current file display when currentIndex changes
    useEffect(() => {
        if (currentFileMetadata) {
            setMetadata({
                title: currentFileMetadata.metadata.title || '',
                artist: currentFileMetadata.metadata.artist || '',
                album: currentFileMetadata.metadata.album || '',
                genre: currentFileMetadata.metadata.genre || '',
                year: currentFileMetadata.metadata.year || undefined,
                cover_art: currentFileMetadata.metadata.cover_art || undefined,
                cover_art_mime_type: currentFileMetadata.metadata.cover_art_mime_type || undefined,
            });
            setCurrentFilename(currentFileMetadata.filename);
            setUpdatedFilename(currentFileMetadata.updatedFilename || null);
            
            if (currentFileMetadata.metadata.cover_art && currentFileMetadata.metadata.cover_art_mime_type) {
                setCoverArtUrl(`data:${currentFileMetadata.metadata.cover_art_mime_type};base64,${currentFileMetadata.metadata.cover_art}`);
            } else {
                setCoverArtUrl(null);
            }
        }
    }, [currentIndex, currentFileMetadata]);    // Handle input changes
    const handleInputChange = (field: keyof AudioMetadata) => (event: React.ChangeEvent<HTMLInputElement>) => {
        const newMetadata = {
            ...metadata,
            [field]: event.target.value
        };
        setMetadata(newMetadata);
        
        if (isBatch) {
            // Apply changes to all selected files
            allFilesMetadata.forEach((fileMetadata, index) => {
                updateFileMetadata(index, { [field]: event.target.value });
            });
        } else {
            updateFileMetadata(currentIndex, { [field]: event.target.value });
        }

        // Trigger auto-save
        debouncedAutoSave(newMetadata);
    };

    // Handle cover art upload
    const handleCoverArtUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                setAlertMessage('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
                setAlertSeverity('error');
                setShowAlert(true);
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
                            if (result) {                                // Extract base64 data
                                const base64Data = result.split(',')[1];
                                const newMetadata = {
                                    ...metadata,
                                    cover_art: base64Data,
                                    cover_art_mime_type: file.type
                                };
                                setMetadata(newMetadata);
                                updateFileMetadata(currentIndex, {
                                    cover_art: base64Data,
                                    cover_art_mime_type: file.type
                                });
                                
                                setCoverArtUrl(result);
                                
                                // Trigger auto-save for cover art
                                debouncedAutoSave(newMetadata);
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
        }    };

    // Auto-save function with debouncing
    const autoSave = useCallback(async (metadataToSave: AudioMetadata) => {
        // Prevent multiple simultaneous saves
        if (isAutoSavingRef.current) {
            return;
        }

        const currentFile = files && files.length > currentIndex ? files[currentIndex] : null;
        if (!currentFile) {
            return;
        }

        isAutoSavingRef.current = true;
        
        try {
            const formData = new FormData();
            formData.append('file', currentFile);
            
            // Clean up the metadata object - remove undefined values and handle nulls properly
            const metadataToSend = {
                title: metadataToSave.title || null,
                artist: metadataToSave.artist || null,
                album: metadataToSave.album || null,
                genre: metadataToSave.genre || null,
                year: metadataToSave.year || null,
                cover_art: metadataToSave.cover_art || null,
                cover_art_mime_type: metadataToSave.cover_art_mime_type || null,
            };
            
            console.log('Auto-saving metadata:', metadataToSend);
            formData.append('metadata', JSON.stringify(metadataToSend));
              const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.UPDATE_TAGS), {
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

            if (result.success) {
                console.log('Metadata auto-saved successfully');
                // Store the updated filename for download
                if (result.updated_filename) {
                    setUpdatedFilename(result.updated_filename);
                    // Update the context with the updated filename
                    setUpdatedFilenameInContext(currentIndex, result.updated_filename);
                }
            } else {
                throw new Error(result.message || 'Failed to update tags');
            }
        } catch (error) {
            console.error('Error auto-saving metadata:', error);
            // Don't show alert for auto-save errors to avoid interrupting user workflow
        } finally {
            isAutoSavingRef.current = false;
        }
    }, [files, currentIndex, setUpdatedFilenameInContext]);

    // Debounced auto-save function
    const debouncedAutoSave = useCallback((metadataToSave: AudioMetadata) => {
        // Clear existing timeout
        if (autoSaveTimeoutRef.current) {
            clearTimeout(autoSaveTimeoutRef.current);
        }

        // Set new timeout for auto-save (1 second delay)
        autoSaveTimeoutRef.current = setTimeout(() => {
            autoSave(metadataToSave);
        }, 1000);
    }, [autoSave]);

    // Clean up timeout on unmount
    useEffect(() => {
        return () => {
            if (autoSaveTimeoutRef.current) {
                clearTimeout(autoSaveTimeoutRef.current);
            }
        };
    }, []);

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
                            size="small"                            onClick={() => {
                                setCoverArtUrl(null);
                                const newMetadata = {
                                    ...metadata,
                                    cover_art: undefined,
                                    cover_art_mime_type: undefined
                                };
                                setMetadata(newMetadata);
                                updateFileMetadata(currentIndex, {
                                    cover_art: undefined,
                                    cover_art_mime_type: undefined
                                });
                                
                                // Trigger auto-save for cover art removal
                                debouncedAutoSave(newMetadata);
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
                        value={metadata.year || ''}                        onChange={(e) => {
                            const value = e.target.value;
                            const yearValue = value ? parseInt(value) : undefined;
                            const newMetadata = {
                                ...metadata,
                                year: yearValue
                            };
                            setMetadata(newMetadata);
                            updateFileMetadata(currentIndex, { year: yearValue });
                            
                            // Trigger auto-save for year
                            debouncedAutoSave(newMetadata);
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
                        onChange={handleInputChange('genre')}                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />
                </div>
            </div><div className="flex flex-col items-center justify-center">
                {allFilesMetadata.length > 1 ? (
                <>
                    <Typography variant="body1" sx={{ mb: 1 }}>
                        {currentFilename || 'No file selected'}
                    </Typography>
                    <Pagination 
                        count={allFilesMetadata.length} 
                        page={currentIndex + 1}
                        onChange={(event, page) => setCurrentIndex(page - 1)}
                        size="medium" 
                        showFirstButton 
                        showLastButton 
                        color="standard" 
                    />
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
                }                <DownloadButtons updatedFilename={updatedFilename} metadata={metadata} allUpdatedFilenames={allUpdatedFilenames} />
            </div>            {showAlert && (
                <Box sx={{ mt: 2 }}>
                    <CustomAlert 
                        message={alertMessage} 
                        severity={alertSeverity}
                        onClose={() => setShowAlert(false)}
                    />
                </Box>
            )}
        </div>
    );
}