import React from 'react';
import { Box, Button, Typography, FormControlLabel, Checkbox } from '@mui/material';
import { useBatch } from '../vars/isBatch';
import { useAllFilesMetadata } from '../vars/allFilesMetadata';
import { useCurrentFileIndex } from '../vars/currentFileIndex';

export default function Toolbar() {
    const { isBatch, setIsBatch } = useBatch();
    const { clearAllMetadata } = useAllFilesMetadata();
    const { setCurrentIndex } = useCurrentFileIndex();

    const handleBatchToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
        setIsBatch(event.target.checked);
    };

    const handleResetAll = () => {
        clearAllMetadata();
        setCurrentIndex(0);
        // Trigger event to clear the editor
        window.dispatchEvent(new CustomEvent('resetEditor'));
    };

    return (
        <Box className="flex justify-left" sx={{ px: 2, py: 2}}>
            <FormControlLabel 
                control={
                    <Checkbox 
                        onChange={handleBatchToggle}
                    />
                } 
                label="Batch Edit" 
            />
            <Button 
                variant="contained" 
                color="warning" 
                size="small" 
                sx={{ ml: 2, height: '2rem' }}
                onClick={handleResetAll}
            >
                <Typography variant="button">Reset All</Typography>
            </Button>
        </Box>
    );
}
