import React from 'react';
import { Box, Button, IconButton, Skeleton, TextField, Pagination, Typography } from '@mui/material';
import UploadIcon from '@mui/icons-material/Upload';
import DownloadButtons from './DownloadButtons';
import { SIZES } from '../constants/sizes';
import { useBatch } from '../vars/isBatch';
import { useNumFiles } from '../vars/numFiles';

export default function TagEditor() {
    const { isBatch } = useBatch();
    const { numFiles } = useNumFiles();

    return (
        <div className="flex flex-col">
            <div className="w-full h-full flex flex-row items-start justify-center gap-6">
                <div className="flex flex-col">
                    <IconButton
                        sx={{
                            width: `${SIZES.artSize}rem`,
                            height: `${SIZES.artSize}rem`,
                            border: '2px solid #ccc',
                            borderRadius: 0
                        }}
                    >
                        <UploadIcon/>
                    </IconButton>
                </div>
                <div className="flex flex-col">
                    <TextField id="title-text" variant="outlined" size="small" label="title" fullWidth sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} />
                    <TextField id="album-text" variant="outlined" size="small" label="album" fullWidth sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} />
                    <TextField id="artist-text" variant="outlined" size="small" label="artist" fullWidth sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} />
                    <TextField id="genre-text" variant="outlined" size="small" label="genre" fullWidth sx={{ mb: 4, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }} />
                    <Button variant="contained" size="small" sx={{mb: 2, width: `${SIZES.inputSize[0]}rem`, height: `${SIZES.inputSize[1]}rem` }}>
                        Save
                    </Button>
                </div>
            </div>
            <div className="flex flex-col items-center justify-center">
                {isBatch ? (
                <>
                    <Typography variant="body1" sx={{ mb: 1 }}>
                        'filename'
                    </Typography>
                    <Pagination count={numFiles} size="medium" showFirstButton showLastButton color="standard" />
                </>
                ) : (
                    <Box sx={{ width: 210, height: 32 }} />
                )
                }
                <DownloadButtons />
            </div>
        </div>
    );
}
