"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface AudioMetadata {
    title?: string;
    artist?: string;
    album?: string;
    genre?: string;
    year?: number;
    track?: string;
    duration?: number;
    cover_art?: string;
    cover_art_mime_type?: string;
}

interface FileMetadata {
    filename: string;
    metadata: AudioMetadata;
    updatedFilename?: string;
    isDownloaded?: boolean;
    storedFilename?: string;
    downloadedFrom?: string;
}

interface AllFilesMetadataContextType {
    allFilesMetadata: FileMetadata[];
    setAllFilesMetadata: (metadata: FileMetadata[]) => void;
    addFileMetadata: (fileMetadata: FileMetadata) => void;
    updateFileMetadata: (index: number, metadata: AudioMetadata) => void;
    updateAllFilesMetadata: (metadata: AudioMetadata) => void;
    setUpdatedFilename: (index: number, filename: string) => void;
    clearAllMetadata: () => void;
}

const AllFilesMetadataContext = createContext<AllFilesMetadataContextType | undefined>(undefined);

interface AllFilesMetadataProviderProps {
    children: ReactNode;
}

export function AllFilesMetadataProvider({ children }: AllFilesMetadataProviderProps) {
    const [allFilesMetadata, setAllFilesMetadata] = useState<FileMetadata[]>([]);

    const addFileMetadata = (fileMetadata: FileMetadata) => {
        setAllFilesMetadata(prev => [...prev, fileMetadata]);
    };

    const updateFileMetadata = (index: number, metadata: AudioMetadata) => {
        setAllFilesMetadata(prev => {
            const updated = [...prev];
            if (updated[index]) {
                updated[index] = {
                    ...updated[index],
                    metadata: { ...updated[index].metadata, ...metadata }
                };
            }
            return updated;
        });
    };

    const updateAllFilesMetadata = (metadata: AudioMetadata) => {
        setAllFilesMetadata(prev => {
            return prev.map(file => ({
                ...file,
                metadata: { ...file.metadata, ...metadata }
            }));
        });
    };

    const setUpdatedFilename = (index: number, filename: string) => {
        setAllFilesMetadata(prev => {
            const updated = [...prev];
            if (updated[index]) {
                updated[index] = {
                    ...updated[index],
                    updatedFilename: filename
                };
            }
            return updated;
        });
    };

    const clearAllMetadata = () => {
        setAllFilesMetadata([]);
    };

    return (        <AllFilesMetadataContext.Provider value={{ 
            allFilesMetadata,
            setAllFilesMetadata,
            addFileMetadata,
            updateFileMetadata,
            updateAllFilesMetadata,
            setUpdatedFilename,
            clearAllMetadata
        }}>
            {children}
        </AllFilesMetadataContext.Provider>
    );
}

export function useAllFilesMetadata() {
    const context = useContext(AllFilesMetadataContext);
    if (context === undefined) {
        throw new Error('useAllFilesMetadata must be used within an AllFilesMetadataProvider');
    }
    return context;
}

export type { FileMetadata };
