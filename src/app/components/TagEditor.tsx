import React, { useState, useEffect } from 'react';
import { Box, Button, TextField, Pagination, Typography } from '@mui/material';
import UploadIcon from '@mui/icons-material/Upload';
import DownloadButtons from './DownloadButtons';
import { SIZES } from '../constants/sizes';
import { useBatch } from '../vars/isBatch';
import { useNumFiles } from '../vars/numFiles';
import { useFiles } from '../vars/files';
import { useAllFilesMetadata, AudioMetadata, FileMetadata } from '../vars/allFilesMetadata';
import { useCurrentFileIndex } from '../vars/currentFileIndex';

export default function TagEditor() {
    const { isBatch } = useBatch();
    const { numFiles } = useNumFiles();
    const { files } = useFiles();
    const { allFilesMetadata, updateFileMetadata, updateAllFilesMetadata, setUpdatedFilename: setUpdatedFilenameInStore } = useAllFilesMetadata();
    const { currentIndex, setCurrentIndex } = useCurrentFileIndex();
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
    const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);// Load metadata when component mounts or when new metadata is available
    useEffect(() => {
        // Listen for metadata loaded events
        const handleMetadataLoaded = (event: CustomEvent) => {
            const { metadata: newMetadata, filename, fileIndex } = event.detail;            setMetadata({
                title: newMetadata.title || '',
                artist: newMetadata.artist || '',
                album: newMetadata.album || '',
                genre: newMetadata.genre || '',
                cover_art: newMetadata.cover_art || undefined,
                cover_art_mime_type: newMetadata.cover_art_mime_type || undefined,
            });
            setCurrentFilename(filename);
            setHasUnsavedChanges(false);
            
            // Set cover art URL if available
            if (newMetadata.cover_art && newMetadata.cover_art_mime_type) {
                setCoverArtUrl(`data:${newMetadata.cover_art_mime_type};base64,${newMetadata.cover_art}`);
            } else {
                setCoverArtUrl(null);
            }

            // Set current index if provided
            if (typeof fileIndex === 'number') {
                setCurrentIndex(fileIndex);
            }
        };        // Listen for reset editor events
        const handleResetEditor = () => {
            setMetadata({
                title: '',
                artist: '',
                album: '',
                genre: '',
            });
            setCurrentFilename('');
            setUpdatedFilename(null);
            setCoverArtUrl(null);
            setHasUnsavedChanges(false);
        };

        window.addEventListener('metadataLoaded', handleMetadataLoaded as EventListener);
        window.addEventListener('resetEditor', handleResetEditor as EventListener);

        return () => {
            window.removeEventListener('metadataLoaded', handleMetadataLoaded as EventListener);
            window.removeEventListener('resetEditor', handleResetEditor as EventListener);
        };
    }, [setCurrentIndex]);    // Load metadata when current index changes
    useEffect(() => {        if (allFilesMetadata.length > 0 && currentIndex < allFilesMetadata.length) {
            const currentFileData = allFilesMetadata[currentIndex];
            setMetadata({
                title: currentFileData.metadata.title || '',
                artist: currentFileData.metadata.artist || '',
                album: currentFileData.metadata.album || '',
                genre: currentFileData.metadata.genre || '',
                year: currentFileData.metadata.year,
                track: currentFileData.metadata.track,
                duration: currentFileData.metadata.duration,
                cover_art: currentFileData.metadata.cover_art,
                cover_art_mime_type: currentFileData.metadata.cover_art_mime_type,
            });
            setCurrentFilename(currentFileData.filename);
            setUpdatedFilename(currentFileData.updatedFilename || null);
            setHasUnsavedChanges(false);
            
            // Set cover art URL if available
            if (currentFileData.metadata.cover_art && currentFileData.metadata.cover_art_mime_type) {
                setCoverArtUrl(`data:${currentFileData.metadata.cover_art_mime_type};base64,${currentFileData.metadata.cover_art}`);
            } else {
                setCoverArtUrl(null);
            }        } else if (allFilesMetadata.length === 0) {
            // Clear everything when no files are loaded
            setMetadata({
                title: '',
                artist: '',
                album: '',
                genre: '',
            });
            setCurrentFilename('');
            setUpdatedFilename(null);
            setCoverArtUrl(null);
            setHasUnsavedChanges(false);
        }
    }, [currentIndex, allFilesMetadata]);    // Handle input changes
    const handleInputChange = (field: keyof AudioMetadata) => (event: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = event.target.value;
        const updatedMetadata = {
            ...metadata,
            [field]: newValue
        };
        
        setMetadata(updatedMetadata);
        setHasUnsavedChanges(true);
        
        if (isBatch) {
            // Update all files when in batch mode
            updateAllFilesMetadata({ [field]: newValue });
        } else {
            // Update only current file
            updateFileMetadata(currentIndex, { [field]: newValue });
        }
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
                                  const updatedMetadata = {
                                    ...metadata,
                                    cover_art: base64Data,
                                    cover_art_mime_type: file.type
                                };
                                  setMetadata(updatedMetadata);
                                setCoverArtUrl(result);
                                setHasUnsavedChanges(true);
                                
                                if (isBatch) {
                                    // Update all files when in batch mode
                                    updateAllFilesMetadata({ 
                                        cover_art: base64Data,
                                        cover_art_mime_type: file.type
                                    });
                                } else {
                                    // Update only current file
                                    updateFileMetadata(currentIndex, { 
                                        cover_art: base64Data,
                                        cover_art_mime_type: file.type
                                    });
                                }
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
            };            reader.readAsDataURL(file);
        }
    };    // Handle save button click
    const handleSave = async () => {
        // Get current file from files array
        const currentFile = files && files.length > 0 ? files[currentIndex] : null;
        
        if (!currentFile) {
            alert('No audio file loaded');
            return;
        }

        setIsSaving(true);

        try {
            console.log('Metadata saved: ', metadata);
            
            // Check if this is a downloaded file
            const currentFileData = allFilesMetadata[currentIndex];
            const isDownloaded = currentFileData?.isDownloaded;
            const storedFilename = currentFileData?.storedFilename;
            
            const formData = new FormData();
            
            if (isDownloaded && storedFilename) {
                // For downloaded files, use the stored filename and different endpoint
                formData.append('stored_filename', storedFilename);
                formData.append('metadata', JSON.stringify(metadata));
                
                console.log('Saving downloaded file with stored filename:', storedFilename);
                console.log('Sending metadata: ', metadata);

                const response = await fetch('/api/upload/update-downloaded-tags', {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    let errorMessage = `HTTP ${response.status}`;
                    
                    try {
                      const errorJson = JSON.parse(errorText);
                      errorMessage = errorJson.detail || errorMessage;
                    } catch {
                      errorMessage = errorText || errorMessage;
                    }
                    
                    console.error('Save failed:', response.status, errorMessage);
                    throw new Error(`Failed to save metadata: ${errorMessage}`);
                }

                const responseData = await response.json();
                
                if (responseData.success) {
                    // Update the metadata store with the new updated filename
                    const newUpdatedFilename = responseData.updated_filename;
                    setUpdatedFilenameInStore(currentIndex, newUpdatedFilename);
                    setUpdatedFilename(newUpdatedFilename);
                    
                    alert('Metadata saved successfully!');
                    setHasUnsavedChanges(false);
                } else {
                    throw new Error('Failed to save metadata');
                }
            } else {
                // For uploaded files, use the original logic
                formData.append('file', currentFile, currentFilename);
                formData.append('metadata', JSON.stringify(metadata));
                
                console.log('Sending metadata: ', metadata);

                const response = await fetch('/api/upload/update-tags', {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    let errorMessage = `HTTP ${response.status}`;
                    
                    try {
                      const errorJson = JSON.parse(errorText);
                      errorMessage = errorJson.detail || errorMessage;
                    } catch {
                      errorMessage = errorText || errorMessage;
                    }
                    
                    console.error('Save failed:', response.status, errorMessage);
                    throw new Error(`Failed to save metadata: ${errorMessage}`);
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = currentFilename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                alert('Metadata saved and file downloaded successfully!');
                setHasUnsavedChanges(false);
            }
        } catch (error) {
            console.error('Error saving metadata:', error);
            const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
            alert(`Error saving metadata: ${errorMessage}`);
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
                    {coverArtUrl && (                        <Button
                            size="small"
                            onClick={() => {
                                setCoverArtUrl(null);
                                const updatedMetadata = {
                                    ...metadata,
                                    cover_art: undefined,
                                    cover_art_mime_type: undefined
                                };                                setMetadata(updatedMetadata);
                                setHasUnsavedChanges(true);
                                
                                if (isBatch) {
                                    // Update all files when in batch mode
                                    updateAllFilesMetadata({ 
                                        cover_art: undefined,
                                        cover_art_mime_type: undefined
                                    });
                                } else {
                                    // Update only current file
                                    updateFileMetadata(currentIndex, { 
                                        cover_art: undefined,
                                        cover_art_mime_type: undefined
                                    });
                                }
                            }}
                            sx={{ mt: 1, fontSize: '0.75rem' }}
                        >
                            Remove Cover
                        </Button>
                    )}
                </div>
                <div className="flex flex-col">                    <TextField 
                        id="title-text" 
                        variant="outlined" 
                        size="small" 
                        label="title" 
                        fullWidth 
                        value={metadata.title || ''}
                        onChange={handleInputChange('title')}
                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />
                    <TextField 
                        id="album-text" 
                        variant="outlined" 
                        size="small" 
                        label="album" 
                        fullWidth 
                        value={metadata.album || ''}
                        onChange={handleInputChange('album')}
                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />                    <TextField 
                        id="artist-text" 
                        variant="outlined" 
                        size="small" 
                        label="artist" 
                        fullWidth 
                        value={metadata.artist || ''}
                        onChange={handleInputChange('artist')}
                        sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} 
                    />
                    <TextField 
                        id="genre-text" 
                        variant="outlined" 
                        size="small" 
                        label="genre" 
                        fullWidth 
                        value={metadata.genre || ''}
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
            </div>            <div className="flex flex-col items-center justify-center">
                {numFiles > 1 ? (
                <>
                    <Typography variant="body1" sx={{ mb: 1 }}>
                        {currentFilename || 'No File Selected'} ({currentIndex + 1} of {numFiles})
                    </Typography>
                    <Pagination 
                        count={numFiles} 
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
                            <Typography variant="body2" sx={{ textAlign: 'center' }}>
                                {currentFilename}
                            </Typography>
                        )}
                    </Box>
                )
                }
                <DownloadButtons updatedFilename={updatedFilename} metadata={metadata} hasUnsavedChanges={hasUnsavedChanges} />
            </div>
        </div>
    );
}
