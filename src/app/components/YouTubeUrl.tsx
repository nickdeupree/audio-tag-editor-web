import React from 'react';
import { TextField, Button, Typography, Box } from '@mui/material';

export default function YouTubeUrl() {
    const [youtubeLink, setYoutubeLink] = React.useState('');

    return (
        <Box className="flex flex-col items-center space-y-4 p-6">
            <Typography variant="h6" component="label" style={{ color: 'var(--color-text)' }}>
                YouTube URL
            </Typography>
            <TextField
                value={youtubeLink}
                onChange={(e) => setYoutubeLink(e.target.value)}
                placeholder="Paste YouTube URL here..."
                variant="outlined"
                size="medium"
                fullWidth
                sx={{ maxWidth: '400px', py: 1 }}
            />
            <Button
                variant="contained"
                color="error"
                onClick={() => console.log('Download:', youtubeLink)}
                sx={{ px: 3, py: 1 }}
            >
                Download & Edit
            </Button>
        </Box>
    );
}