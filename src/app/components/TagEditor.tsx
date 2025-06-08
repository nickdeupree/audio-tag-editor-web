import React from 'react';
import TagEditorSkele from '../skeletons/TagEditorSkele';

export default function TagEditor() {
    const artSize = 20;
    const inputSize = [15, 2.5] as const;
    const labelSize = [5, 1.25] as const;
    const buttonSize = [10, 3] as const;

    return (
        <TagEditorSkele />
    );
}