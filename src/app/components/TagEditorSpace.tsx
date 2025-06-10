import React from 'react';
import TagEditorSkele from '../skeletons/TagEditorSkele';
import TagEditor from './TagEditor';
import Toolbar from './Toolbar';
import { useAddingFile } from '../vars/addingFile';
import { useFiles } from '../vars/files';
import { useAllFilesMetadata } from '../vars/allFilesMetadata';

export default function TagEditorSpace() {
    const { isAddingFile } = useAddingFile();
    const { files } = useFiles();
    const { allFilesMetadata } = useAllFilesMetadata();
    
    // Check if we have either uploaded files or downloaded files (from YouTube/SoundCloud)
    const hasAnyFiles = (files && files.length > 0) || (allFilesMetadata && allFilesMetadata.length > 0);
    
    // Show skeleton when actively adding files AND no files exist yet
    const showSkeleton = isAddingFile && !hasAnyFiles;
    return (
        <div className="flex flex-col h-full">
            <Toolbar />
            <div className="my-2" />
            {showSkeleton ? (
            <TagEditorSkele />
            ) : (
            <TagEditor />
            )}
        </div>
    );
}
