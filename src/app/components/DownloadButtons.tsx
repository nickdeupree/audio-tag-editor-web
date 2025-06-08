import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { SIZES } from '../constants/sizes';

export default function DownloadButtons() {
    
    return (
        <div className="flex flex-row justify-center mt-6 gap-4">
            <Button variant="contained" size="large" sx={{ width: `${SIZES.buttonSize[0]}rem`, height: `${SIZES.buttonSize[1]}rem` }}>
                Download
            </Button>
            <Button variant="contained" size="medium" sx={{ width: `${SIZES.buttonSize[0]}rem`, height: `${SIZES.buttonSize[1]}rem` }}>
                Upload to YTM
            </Button>
        </div>
    );
}