"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface CurrentFileIndexContextType {
    currentIndex: number;
    setCurrentIndex: (index: number) => void;
    goToNext: () => void;
    goToPrevious: () => void;
    goToFirst: () => void;
    goToLast: () => void;
}

const CurrentFileIndexContext = createContext<CurrentFileIndexContextType | undefined>(undefined);

interface CurrentFileIndexProviderProps {
    children: ReactNode;
}

export function CurrentFileIndexProvider({ children }: CurrentFileIndexProviderProps) {
    const [currentIndex, setCurrentIndex] = useState(0);

    const goToNext = () => {
        setCurrentIndex(prev => prev + 1);
    };

    const goToPrevious = () => {
        setCurrentIndex(prev => Math.max(0, prev - 1));
    };

    const goToFirst = () => {
        setCurrentIndex(0);
    };

    const goToLast = () => {
        setCurrentIndex(prev => prev); // Will be set properly when we know the total
    };

    return (
        <CurrentFileIndexContext.Provider value={{ 
            currentIndex, 
            setCurrentIndex, 
            goToNext, 
            goToPrevious, 
            goToFirst, 
            goToLast 
        }}>
            {children}
        </CurrentFileIndexContext.Provider>
    );
}

export function useCurrentFileIndex() {
    const context = useContext(CurrentFileIndexContext);
    if (context === undefined) {
        throw new Error('useCurrentFileIndex must be used within a CurrentFileIndexProvider');
    }
    return context;
}
