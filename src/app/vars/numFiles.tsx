"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface NumFilesContextType {
    numFiles: number;
    setNumFiles: (value: number) => void;
    incrementNumFiles: () => void;
    decrementNumFiles: () => void;
    clearNumFiles: () => void;
}

const NumFilesContext = createContext<NumFilesContextType | undefined>(undefined);

interface NumFilesProviderProps {
    children: ReactNode;
}
export function NumFilesProvider({ children }: NumFilesProviderProps) {
    const [numFiles, setNumFiles] = useState(0);

    const incrementNumFiles = () => {
        setNumFiles(prev => prev + 1);
    };

    const decrementNumFiles = () => {
        setNumFiles(prev => Math.max(0, prev - 1));
    };

    const clearNumFiles = () => {
        setNumFiles(0);
    };

    return (
        <NumFilesContext.Provider value={{ numFiles, setNumFiles, incrementNumFiles, decrementNumFiles, clearNumFiles }}>
            {children}
        </NumFilesContext.Provider>
    );
}

export function useNumFiles() {
    const context = useContext(NumFilesContext);
    if (context === undefined) {
        throw new Error('useNumFiles must be used within a NumFilesProvider');
    }
    return context;
}