import React from 'react';
import { Button, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';


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
    const [file, setFile] = React.useState<File | null>(null);


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
            startIcon={<CloudUploadIcon />}
            sx={{ px: 3, py: 1 }}
            >
            Upload files
            <VisuallyHiddenInput
                type="file"
                accept="audio/*"
                onChange={(event) => console.log(event.target.files)}
                multiple
                sx={{px: 3, py: 1 }}
            />
            </Button>
        </Box>
    );
}