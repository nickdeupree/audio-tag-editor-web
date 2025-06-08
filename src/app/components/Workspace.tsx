"use client";

import * as React from 'react';
import OptionsColumn from './OptionsColumn';
import InputOption from './InputOption';
import UploadFile from './UploadFile';
import TagEditor from './TagEditor';

export default function Workspace() {
    return (
        <div className="w-full max-w-6xl min-h-[600px] rounded-xl shadow-2xl overflow-hidden flex flex-col" style={{ backgroundColor: 'var(--color-background)' }}>
            <div className="flex-1 flex min-h-[500px] flex-col md:flex-row">
                <div className="w-full md:w-80 border-b md:border-b-0 md:border-r p-6 flex flex-col" style={{ backgroundColor: 'var(--color-background)', borderColor: 'var(--color-muted)', filter: 'brightness(0.98)' }}>
                    <InputOption />
                    <OptionsColumn />
                </div>
                <div className="flex-1 p-6 md:p-8 flex items-center justify-center" style={{ backgroundColor: 'var(--color-background)' }}>
                    <TagEditor />
                </div>
            </div>
        </div>
    );
}
