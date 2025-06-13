import React from 'react';
import { Button, Box, Typography } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CustomAlert from './CustomAlert';
import { useBatch } from '../vars/isBatch';
import { useFiles } from '../vars/files';
import { useAddingFile } from '../vars/addingFile';
import { getApiUrl, API_CONFIG } from '../config/api';

export default function UploadFile() {
    const { setFiles } = useFiles();
    const { setIsBatch } = useBatch();
    const { isAddingFile, setIsAddingFile } = useAddingFile();

    // Alert state
    const [alertMessage, setAlertMessage] = React.useState<string>('');
    const [alertSeverity, setAlertSeverity] = React.useState<'error' | 'warning' | 'info' | 'success'>('info');
    const [showAlert, setShowAlert] = React.useState<boolean>(false);
    
    // Staged files state
    const [stagedFiles, setStagedFiles] = React.useState<File[]>([]);

    const onDrop = React.useCallback((acceptedFiles: File[]) => {
        setStagedFiles(prev => [...prev, ...acceptedFiles]);
    }, []);

    const processStagedFiles = async () => {
        if (stagedFiles.length === 0) return;
        
        try {
            setIsAddingFile(true);
            
            // Convert File[] to FileList
            const fileList = {
                item: (index: number) => stagedFiles[index] || null,
                ...stagedFiles
            } as FileList;
            
            setFiles(fileList);
            
            if (stagedFiles.length > 1) {
                setIsBatch(true);
            }

            // Send files to backend
            try {
                const formData = new FormData();
                
                // Append all files to the 'files' field
                for (let i = 0; i < stagedFiles.length; i++) {
                    formData.append('files', stagedFiles[i]);
                }                console.log(`Uploading ${stagedFiles.length} file(s)`);

                const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.UPLOAD), {
                    method: 'POST',
                    body: formData,
                });

                console.log('Response status:', response.status);

                if (response.ok) {
                    const result = await response.json();
                    console.log('Upload successful:', result);                                        
                    if (result.metadata || result.all_files_metadata) {
                        console.log('received: ', result);
                        
                        // Trigger a custom event to notify TagEditor
                        window.dispatchEvent(new CustomEvent('metadataLoaded', { 
                            detail: {
                                metadata: result.metadata,
                                filename: result.filename,
                                platform: result.platform,
                                originalUrl: result.original_url,
                                all_files_metadata: result.all_files_metadata
                            }
                        }));
                        
                        // Clear staged files after successful upload
                        setStagedFiles([]);
                    }
                } else {
                    const errorText = await response.text();
                    console.error('Upload failed:', errorText);
                    setAlertMessage(`Upload failed: ${errorText}`);
                    setAlertSeverity('error');
                    setShowAlert(true);
                }            } catch (uploadError: unknown) {
                console.error('Error uploading files:', uploadError);
                setAlertMessage(`Upload error: ${uploadError instanceof Error ? uploadError.message : 'Unknown upload error'}`);
                setAlertSeverity('error');
                setShowAlert(true);
            }
        } catch (error: unknown) {
            console.error('General error in file upload:', error);
            setAlertMessage(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
            setAlertSeverity('error');
            setShowAlert(true);
        } finally {
            setIsAddingFile(false);
        }
    };

    const clearStagedFiles = () => {
        setStagedFiles([]);
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'audio/*': ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']
        },
        multiple: true,
        disabled: isAddingFile
    });

    return (
        <Box className="flex flex-col items-center space-y-6 p-6">
            <Box
                {...getRootProps()}
                sx={{
                    border: '2px dashed',
                    borderColor: isDragActive ? 'primary.main' : 'grey.400',
                    borderRadius: 2,
                    p: 4,
                    textAlign: 'center',
                    cursor: isAddingFile ? 'not-allowed' : 'pointer',
                    backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                    transition: 'all 0.2s ease-in-out',
                    width: '100%',
                    maxWidth: '400px',
                    opacity: isAddingFile ? 0.6 : 1
                }}
            >
                <input {...getInputProps()} />
                <CloudUploadIcon sx={{ fontSize: 48, color: 'grey.500', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                    {isDragActive ? 'Drop files here' : 'Upload Audio Files'}
                </Typography>
            </Box>

            {stagedFiles.length > 0 && (
                <Box sx={{ textAlign: 'center', maxWidth: '400px', width: '100%' }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Selected files:
                    </Typography>
                    <Box sx={{ maxHeight: '100px', overflowY: 'auto'}}>
                        {stagedFiles.map((file, index) => (
                            <Typography key={index} variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                                {file.name}
                            </Typography>
                        ))}
                    </Box>
                </Box>
            )}

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                {stagedFiles.length > 0 && (
                    <Button
                        variant="outlined"
                        onClick={clearStagedFiles}
                        disabled={isAddingFile}
                        size="medium"
                    >
                        Clear
                    </Button>
                )}
                <Button
                    variant="contained"
                    onClick={stagedFiles.length > 0 ? processStagedFiles : undefined}
                    disabled={isAddingFile || stagedFiles.length === 0}
                    sx={{}}
                >
                    Continue to Edit {stagedFiles.length > 0 ? `(${stagedFiles.length})` : ''}
                </Button>
            </Box>
            
            {showAlert && (
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