import React from 'react';
import { Button, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import UploadIcon from '@mui/icons-material/Upload';
import { useBatch } from '../vars/isBatch';
import { useNumFiles } from '../vars/numFiles';
import { useFiles } from '../vars/files';
import { useAllFilesMetadata } from '../vars/allFilesMetadata';
import { useCurrentFileIndex } from '../vars/currentFileIndex';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

export default function UploadFile() {
    const { files, setFiles } = useFiles();
    const { setIsBatch } = useBatch();
    const { setNumFiles } = useNumFiles();
    const { setAllFilesMetadata, clearAllMetadata } = useAllFilesMetadata();
    const { setCurrentIndex } = useCurrentFileIndex();
    const [isLoading, setIsLoading] = React.useState(false);

    return (
        <Box className="flex flex-col items-center space-y-6 p-6">
            <Typography variant="h6" component="label" style={{ color: 'var(--color-text)' }}>
                {files && files.length ? 'Add a File' : 'Upload a File'}
            </Typography>
            { files && files.length > 0 && (
                <Button
                component="label"
                role={undefined}
                variant="contained"
                tabIndex={-1}
                startIcon={<UploadIcon />}
                sx={{ px: 3, py: 1 }}
                disabled={isLoading}
            >
                Add files
                <VisuallyHiddenInput
                    type="file"
                    accept="audio/*" onChange={async (event) => {
                        try {
                            setIsLoading(true);
                            const additionalFiles = event.target.files;
                            const newFiles: File[] = additionalFiles ? Array.from(additionalFiles) : [];
                            const prevFilesArray: File[] = files ? Array.from(files) : [];
                            const combinedFiles = [...prevFilesArray, ...newFiles];
                            setFiles(combinedFiles as any);
                            clearAllMetadata();
                            setCurrentIndex(0);
                            
                            if (combinedFiles && combinedFiles.length > 1) {
                                setIsBatch(true);
                                setNumFiles(combinedFiles.length);
                            } else {
                                setIsBatch(false);
                                setNumFiles(combinedFiles ? combinedFiles.length : 0);
                            }                            // Send files to backend
                            if (combinedFiles && combinedFiles.length > 0) {
                                try {
                                    
                                    const formData = new FormData();

                                    // Append all files to the 'files' field
                                    for (let i = 0; i < combinedFiles.length; i++) {
                                        formData.append('files', combinedFiles[i]);
                                    }

                                    console.log(`Uploading ${combinedFiles.length} file(s)`);

                                    const response = await fetch('http://localhost:8000/upload/', {
                                        method: 'POST',
                                        body: formData,
                                    });

                                    console.log('Response status:', response.status);

                                    if (response.ok) {
                                        const result = await response.json();
                                        console.log('Upload successful:', result);
                                        
                                        if (result.files) {
                                            // Store metadata for all files
                                            const allMetadata = result.files.map((file: any) => ({
                                                filename: file.filename,
                                                metadata: file.metadata || {},
                                                success: file.success
                                            }));
                                            
                                            setAllFilesMetadata(allMetadata);
                                            
                                            // Trigger event for first file to load in editor
                                            const firstSuccessfulFile = result.files.find((f: any) => f.success);
                                            if (firstSuccessfulFile) {
                                                window.dispatchEvent(new CustomEvent('metadataLoaded', { 
                                                    detail: { 
                                                        metadata: firstSuccessfulFile.metadata, 
                                                        filename: firstSuccessfulFile.filename,
                                                        fileIndex: 0
                                                    }
                                                }));
                                            }
                                        }
                                    } else {
                                        const errorText = await response.text();
                                        console.error('Upload failed:', errorText);
                                        alert(`Upload failed: ${errorText}`);
                                    }
                                } catch (uploadError: any) {
                                    console.error('Error uploading files:', uploadError);
                                    alert(`Upload error: ${uploadError?.message || 'Unknown upload error'}`);
                                }
                            }
                        } catch (error: any) {
                            console.error('General error in file upload:', error);
                            alert(`Error: ${error?.message || 'Unknown error'}`);
                        } finally {
                            setIsLoading(false);
                        }
                    }}
                    multiple
                />
            </Button>
                )
            }
            { (!files || files.length === 0) &&
                (
                    <Button
                component="label"
                role={undefined}
                variant="contained"
                tabIndex={-1}
                startIcon={<UploadIcon />}
                sx={{ px: 3, py: 1 }}
                disabled={isLoading}
            >
                Upload files
                <VisuallyHiddenInput
                    type="file"
                    accept="audio/*" onChange={async (event) => {
                        try {
                            setIsLoading(true);
                            const selectedFiles = event.target.files;
                            setFiles(selectedFiles);
                            clearAllMetadata();
                            setCurrentIndex(0);
                            
                            if (selectedFiles && selectedFiles.length > 1) {
                                setIsBatch(true);
                                setNumFiles(selectedFiles.length);
                            } else {
                                setIsBatch(false);
                                setNumFiles(selectedFiles ? selectedFiles.length : 0);
                            }                            // Send files to backend
                            if (selectedFiles && selectedFiles.length > 0) {
                                try {
                                    const formData = new FormData();

                                    // Append all files to the 'files' field
                                    for (let i = 0; i < selectedFiles.length; i++) {
                                        formData.append('files', selectedFiles[i]);
                                    }

                                    console.log(`Uploading ${selectedFiles.length} file(s)`);

                                    const response = await fetch('http://localhost:8000/upload/', {
                                        method: 'POST',
                                        body: formData,
                                    });

                                    console.log('Response status:', response.status);

                                    if (response.ok) {
                                        const result = await response.json();
                                        console.log('Upload successful:', result);
                                        
                                        if (result.files) {
                                            // Store metadata for all files
                                            const allMetadata = result.files.map((file: any) => ({
                                                filename: file.filename,
                                                metadata: file.metadata || {},
                                                success: file.success
                                            }));
                                            
                                            setAllFilesMetadata(allMetadata);
                                            
                                            // Trigger event for first file to load in editor
                                            const firstSuccessfulFile = result.files.find((f: any) => f.success);
                                            if (firstSuccessfulFile) {
                                                window.dispatchEvent(new CustomEvent('metadataLoaded', { 
                                                    detail: { 
                                                        metadata: firstSuccessfulFile.metadata, 
                                                        filename: firstSuccessfulFile.filename,
                                                        fileIndex: 0
                                                    }
                                                }));
                                            }
                                        }
                                    } else {
                                        const errorText = await response.text();
                                        console.error('Upload failed:', errorText);
                                        alert(`Upload failed: ${errorText}`);
                                    }
                                } catch (uploadError: any) {
                                    console.error('Error uploading files:', uploadError);
                                    alert(`Upload error: ${uploadError?.message || 'Unknown upload error'}`);
                                }
                            }
                        } catch (error: any) {
                            console.error('General error in file upload:', error);
                            alert(`Error: ${error?.message || 'Unknown error'}`);
                        } finally {
                            setIsLoading(false);
                        }
                    }}
                    multiple
                />
            </Button>
                )
                
            }
        </Box>
    );
}