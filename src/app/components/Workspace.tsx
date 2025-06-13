"use client";

import * as React from 'react';
import { Button } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import OptionsColumn from './OptionsColumn';
import InputOption from './InputOption';
import TagEditorSpace from './TagEditorSpace';
import { useFiles } from '../vars/files';
import { useAllFilesMetadata, FileMetadata } from '../vars/allFilesMetadata';
import { useCurrentFileIndex } from '../vars/currentFileIndex';
import { useAddingFile } from '../vars/addingFile';
import { getApiUrl, API_CONFIG } from '../config/api';

export default function Workspace() {
    const { setFiles } = useFiles();
    const { allFilesMetadata, addFileMetadata, setAllFilesMetadata } = useAllFilesMetadata();
    const { setCurrentIndex } = useCurrentFileIndex();
    const { isAddingFile } = useAddingFile();
    
    // Show tag editor when we have any files OR when actively adding files
    const hasFiles = (allFilesMetadata && allFilesMetadata.length > 0) || isAddingFile;

    // Clear cache when component first loads
    React.useEffect(() => {
        const clearCacheOnLoad = async () => {
            try {
                console.log('Clearing cache on page load...');
                const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.CLEAR_CACHE), {
                    method: 'POST',
                });
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('Cache cleared on load:', result.message);
                } else {
                    console.warn('Cache clear on load failed:', response.status);
                }
            } catch (error) {
                console.warn('Cache clear on load error:', error);
                // Don't throw error since cache clearing is optional
            }
        };
        
        clearCacheOnLoad();
    }, []); // Empty dependency array means this runs once on component mount

    // Listen for metadata loaded events from YouTube/SoundCloud downloads
    React.useEffect(() => {
        const handleMetadataLoaded = (event: CustomEvent) => {
            const { metadata: newMetadata, filename, platform: filePlatform, all_files_metadata, stored_filename: singleFileStoredFilename } = event.detail;
            
            if (all_files_metadata && Array.isArray(all_files_metadata) && all_files_metadata.length > 0) {
                // Handle multiple files (file upload)
                const currentAllFiles = allFilesMetadata; // Capture current state for calculating new index
                const newFiles: FileMetadata[] = all_files_metadata.map((fileData: any) => ({
                    filename: fileData.filename,
                    storedFilename: fileData.stored_filename, 
                    metadata: fileData.metadata,
                    isDownloaded: false,
                    updatedFilename: undefined,
                    downloadedFrom: undefined,
                }));

                setAllFilesMetadata([...currentAllFiles, ...newFiles]);
                
                if (currentAllFiles.length === 0 && newFiles.length > 0) {
                    setCurrentIndex(0); 
                } else if (newFiles.length > 0) {
                    setCurrentIndex(currentAllFiles.length); // Set to the index of the first new file
                }
            } else if (filename && newMetadata) {
                // Handle single file (YouTube/SoundCloud download)
                const currentAllFiles = allFilesMetadata;
                const newFile: FileMetadata = {
                    filename: filename, 
                    storedFilename: singleFileStoredFilename || filename, 
                    metadata: newMetadata,
                    isDownloaded: true,
                    downloadedFrom: filePlatform || 'unknown',
                    updatedFilename: undefined,
                };
                
                // addFileMetadata already uses the functional update form, so this is fine
                addFileMetadata(newFile); 
                setCurrentIndex(currentAllFiles.length); // Set to the index of the newly added file
            }
        };

        window.addEventListener('metadataLoaded', handleMetadataLoaded as EventListener);
        
        return () => {
            window.removeEventListener('metadataLoaded', handleMetadataLoaded as EventListener);
        };
    // Ensure all dependencies that can change the logic are included.
    // allFilesMetadata itself is a dependency because its length is used to calculate the next index.
    }, [addFileMetadata, setAllFilesMetadata, setCurrentIndex, allFilesMetadata]);

    function closeWorkspace() {
        setAllFilesMetadata([]);
        setCurrentIndex(0);
        setFiles(null);
        fetch(getApiUrl(API_CONFIG.ENDPOINTS.CLEAR_CACHE), {
            method: 'POST',
        }).catch((error) => {
            console.warn('Cache clear on close error:', error);
        });
    }

    return (
        <div className="w-full max-w-6xl min-h-[600px] rounded-xl shadow-2xl overflow-hidden flex flex-col relative" style={{ backgroundColor: 'var(--color-background)' }}>
            <div className="flex-1 flex min-h-[500px] flex-col md:flex-row">
                <div 
                    className={`${
                        hasFiles 
                            ? "w-full md:w-80 border-b md:border-b-0 md:border-r transition-all duration-300 ease-in-out" 
                            : "w-full transition-all duration-300 ease-in-out"
                    } p-6 flex flex-col`} 
                    style={{ backgroundColor: 'var(--color-background)', borderColor: 'var(--color-muted)', filter: 'brightness(0.98)' }}
                >
                    <InputOption />
                    <OptionsColumn />
                </div>
                {hasFiles && (
                    <div 
                        className="flex-1 opacity-100 translate-x-0 transition-all duration-300 ease-in-out p-6 md:p-8 flex items-center justify-center relative"
                        style={{ backgroundColor: 'var(--color-background)' }}
                    >
                        <Button
                            className="!absolute !top-4 !right-4 !z-10 !min-w-8 !w-8 !h-8 !p-0"
                            variant="text"
                            color="inherit"
                            onClick={() => {
                                closeWorkspace();
                            }}
                            aria-label="Close workspace"
                            sx={{
                                opacity: 0.6,
                                '&:hover': {
                                    opacity: 1,
                                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                                    '& .MuiSvgIcon-root': {
                                        color: 'red'
                                    }
                                }
                            }}
                        >
                            <CloseIcon sx={{ fontSize: 20 }} />
                        </Button>
                        <TagEditorSpace />
                    </div>
                )}
            </div>
        </div>
    );
}
