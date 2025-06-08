import React from 'react';
import TagEditorSkele from '../skeletons/TagEditorSkele';
import TagEditor from './TagEditor';
import Toolbar from './Toolbar';
export default function TagEditorSpace() {
    const [loading, setLoading] = React.useState(false);

    return (
        <div className="flex flex-col h-full">
            <Toolbar />
            <div className="my-2" />
            {loading ? (
            <TagEditorSkele />
            ) : (
            <TagEditor />
            )}
        </div>
    );
}
