"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface FilesContextType {
    files: FileList | null;
    setFiles: (files: FileList | null) => void;
    clearFiles: () => void;
    addFile: (file: File) => void;
}

const FilesContext = createContext<FilesContextType | undefined>(undefined);

interface FilesProviderProps {
    children: ReactNode;
}

export function FilesProvider({ children }: FilesProviderProps) {
    const [files, setFilesState] = useState<FileList | null>(null);

    const setFiles = (newFiles: FileList | null) => {
        setFilesState(newFiles);
    };

    const clearFiles = () => {
        setFilesState(null);
    };

    const addFile = (file: File) => {
        if (files) {
            const newFiles = Array.from(files);
            newFiles.push(file);
            const dataTransfer = new DataTransfer();
            newFiles.forEach(f => dataTransfer.items.add(f));
            setFilesState(dataTransfer.files);
        } else {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            setFilesState(dataTransfer.files);
        }
    };

    return (
        <FilesContext.Provider value={{ files, setFiles, clearFiles, addFile }}>
            {children}
        </FilesContext.Provider>
    );
}
export function useFiles() {
    const context = useContext(FilesContext);
    if (context === undefined) {
        throw new Error('useFiles must be used within a FilesProvider');
    }
    return context;
}