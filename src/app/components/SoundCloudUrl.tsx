import React from 'react';
import { TextField, Button, Typography, Box } from '@mui/material';

export default function SoundCloudUrl() {
    const [soundcloudLink, setSoundcloudLink] = React.useState('');

    return (
        <Box className="flex flex-col items-center space-y-4 p-6">
            <Typography variant="h6" component="label" style={{ color: 'var(--color-text)' }}>
                SoundCloud URL
            </Typography>
            <TextField
                value={soundcloudLink}
                onChange={(e) => setSoundcloudLink(e.target.value)}
                placeholder="SoundCloud URL"
                variant="outlined"
                size="medium"
                fullWidth
                sx={{ maxWidth: '400px', py: 1 }}
            />
            <Button
                variant="contained"
                onClick={() => console.log('Download:', soundcloudLink)}
                sx={{ 
                    px: 3, 
                    py: 1,
                    backgroundColor: '#ff5500',
                    '&:hover': {
                        backgroundColor: '#e64900'
                    }
                }}
            >
                Download & Edit
            </Button>
        </Box>
    );
}