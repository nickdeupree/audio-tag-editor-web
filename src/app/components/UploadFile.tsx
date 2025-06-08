import React from 'react';
import { Button, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import UploadIcon from '@mui/icons-material/Upload';
import { useBatch } from '../vars/isBatch';
import { useNumFiles } from '../vars/numFiles';


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
    const [files, setFiles] = React.useState<FileList | null>(null);
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
            loading={isLoading}
            >
            Upload files
            <VisuallyHiddenInput
                type="file"
                accept="audio/*"
                onChange={(event) => {
                    setIsLoading(true);
                    const selectedFiles = event.target.files;
                    setFiles(selectedFiles);
                    if (selectedFiles && selectedFiles.length > 1) {
                        setIsBatch(true);
                        setNumFiles(selectedFiles.length);
                    }
                    setIsLoading(false);

                }}
                multiple
                sx={{px: 3, py: 1 }}
            />
            </Button>
        </Box>
    );
}