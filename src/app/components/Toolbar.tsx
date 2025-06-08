import React from 'react';
import { Box, Button, Typography, FormControlLabel } from '@mui/material';

export default function Toolbar() {
    return (
        <Box className="flex justify-left" sx={{ px: 2, py: 2}}>
            <FormControlLabel control={<input type="checkbox"/>} label="Batch Edit" />
            <Button variant="contained" color="warning" size="small" sx={{ ml: 2, height: '2rem' }}>
                <Typography variant="button">Reset All</Typography>
            </Button>
        </Box>
    );
}
