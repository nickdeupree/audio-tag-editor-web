"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AddingFileContextType {
    isAddingFile: boolean;
    setIsAddingFile: (value: boolean) => void;
    toggleIsAddingFile: () => void;
}

const AddingFileContext = createContext<AddingFileContextType | undefined>(undefined);

interface AddingFileProviderProps {
    children: ReactNode;
}

export function AddingFileProvider({ children }: AddingFileProviderProps) {
    const [isAddingFile, setIsAddingFile] = useState(false);

    const toggleIsAddingFile = () => {
        setIsAddingFile(prev => !prev);
    };

    return (
        <AddingFileContext.Provider value={{ isAddingFile, setIsAddingFile, toggleIsAddingFile }}>
            {children}
        </AddingFileContext.Provider>
    );
}

export function useAddingFile() {
    const context = useContext(AddingFileContext);
    if (context === undefined) {
        throw new Error('useAddingFile must be used within a AddingFileProvider');
    }
    return context;
}