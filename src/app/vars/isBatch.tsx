"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface BatchContextType {
    isBatch: boolean;
    setIsBatch: (value: boolean) => void;
    toggleIsBatch: () => void;
}

const BatchContext = createContext<BatchContextType | undefined>(undefined);

interface BatchProviderProps {
    children: ReactNode;
}

export function BatchProvider({ children }: BatchProviderProps) {
    const [isBatch, setIsBatch] = useState(false);

    const toggleIsBatch = () => {
        setIsBatch(prev => !prev);
    };

    return (
        <BatchContext.Provider value={{ isBatch, setIsBatch, toggleIsBatch }}>
            {children}
        </BatchContext.Provider>
    );
}

export function useBatch() {
    const context = useContext(BatchContext);
    if (context === undefined) {
        throw new Error('useBatch must be used within a BatchProvider');
    }
    return context;
}