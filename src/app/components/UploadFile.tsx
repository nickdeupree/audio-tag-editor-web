import React from 'react';
import { Button, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import UploadIcon from '@mui/icons-material/Upload';
import { useBatch } from '../vars/isBatch';
import { useNumFiles } from '../vars/numFiles';
import { useFiles } from '../vars/files';

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
    const { setFiles } = useFiles();
    const { setIsBatch } = useBatch();
    const { setNumFiles } = useNumFiles();
    const [isLoading, setIsLoading] = React.useState(false);

    return (
        <Box className="flex flex-col items-center space-y-6 p-6">
            <Typography variant="h6" component="label" style={{ color: 'var(--color-text)' }}>
                Upload a File
            </Typography>
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
                    accept="audio/*"
                    onChange={async (event) => {
                        try {
                            setIsLoading(true);
                            const selectedFiles = event.target.files;
                            setFiles(selectedFiles);
                            
                            if (selectedFiles && selectedFiles.length > 1) {
                                setIsBatch(true);
                                setNumFiles(selectedFiles.length);
                            }

                            // Send files to backend
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
                                        if (result.metadata) {
                                            console.log('received: ', result.metadata);
                                            
                                            // Trigger a custom event to notify TagEditor
                                            window.dispatchEvent(new CustomEvent('metadataLoaded', { 
                                                detail: { metadata: result.metadata, filename: result.filename }
                                            }));
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
        </Box>
    );
}