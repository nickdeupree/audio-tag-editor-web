import React from "react";
import { Skeleton } from "@mui/material";
import { SIZES } from '../constants/sizes';

export default function TagEditorSkele() {
    return (
        <div className="flex flex-col">
            <div className="w-full h-full flex flex-row items-start justify-center gap-6">
                <div className="flex flex-col">
                    <Skeleton variant="rounded" width={`${SIZES.artSize}rem`} height={`${SIZES.artSize}rem`} />
                </div>
                <div className="flex flex-col">
                    <Skeleton 
                        variant="rounded" 
                        width={`${SIZES.inputSize[0]}rem`} 
                        height={`${SIZES.inputSize[1]}rem`} 
                        sx={{ mb: 4 }}
                    />
                    <Skeleton 
                        variant="rounded" 
                        width={`${SIZES.inputSize[0]}rem`} 
                        height={`${SIZES.inputSize[1]}rem`} 
                        sx={{ mb: 4 }}
                    />
                    <Skeleton 
                        variant="rounded" 
                        width={`${SIZES.inputSize[0]}rem`} 
                        height={`${SIZES.inputSize[1]}rem`} 
                        sx={{ mb: 4 }}
                    />
                    <Skeleton 
                        variant="rounded" 
                        width={`${SIZES.inputSize[0]}rem`} 
                        height={`${SIZES.inputSize[1]}rem`} 
                        sx={{ mb: 4 }}
                    />
                    <Skeleton 
                        variant="rounded" 
                        width={`${SIZES.inputSize[0]}rem`} 
                        height={`${SIZES.inputSize[1]}rem`} 
                        sx={{ mb: 4 }}
                    />
                </div>
            </div>
            <div className="flex flex-col items-center justify-center">
                {/* Skeleton for filename/pagination area */}
                <Skeleton 
                    variant="text" 
                    width={210} 
                    height={32} 
                    sx={{ mb: 1 }}
                />
                <div className="flex flex-row justify-center gap-4">
                    <Skeleton 
                        variant="rounded" 
                        width={`${SIZES.buttonSize[0]}rem`} 
                        height={`${SIZES.buttonSize[1]}rem`}
                    />
                    <Skeleton 
                        variant="rounded" 
                        width={`${SIZES.buttonSize[0]}rem`} 
                        height={`${SIZES.buttonSize[1]}rem`}
                    />
                </div>
            </div>
        </div>
    );
}