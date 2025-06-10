import React from 'react';
import { Box, FormControlLabel, Skeleton } from '@mui/material';
import { useBatch } from '../vars/isBatch';
import { useFiles } from '../vars/files';
import { useAllFilesMetadata } from '../vars/allFilesMetadata';
import { useAddingFile } from '../vars/addingFile';

export default function Toolbar() {
    const { isBatch, toggleIsBatch } = useBatch();
    const { files } = useFiles();
    const { allFilesMetadata} = useAllFilesMetadata();
    const { isAddingFile } = useAddingFile();
        
    const hasAnyFiles = (files && files.length > 0) || (allFilesMetadata && allFilesMetadata.length > 0);    
    const showSkeleton = isAddingFile && !hasAnyFiles;

    return (
        <Box className="flex justify-left" sx={{ px: 2, py: 2}}>
            { showSkeleton ? (
                <Skeleton variant="rounded" width={120} height={24}/>
                )
            :
            (
                <FormControlLabel control={<input type="checkbox" checked={isBatch} onChange={toggleIsBatch} />} label="Batch Edit" />
            )
            }
            

            
            {/* <Button variant="contained" color="warning" size="small" sx={{ ml: 2, height: '2rem' }}>
                <Typography variant="button">Reset All</Typography>
            </Button> */}
        </Box>
    );
}
