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
                    <Skeleton variant="rounded" width={`${SIZES.inputSize[0]}rem`} height={`${SIZES.inputSize[1]}rem`} className="mb-4" />
                    <Skeleton variant="rounded" width={`${SIZES.inputSize[0]}rem`} height={`${SIZES.inputSize[1]}rem`} className="mb-4" />
                    <Skeleton variant="rounded" width={`${SIZES.inputSize[0]}rem`} height={`${SIZES.inputSize[1]}rem`} className="mb-4" />
                    <Skeleton variant="rounded" width={`${SIZES.inputSize[0]}rem`} height={`${SIZES.inputSize[1]}rem`} className="mb-4" />
                    <Skeleton variant="rounded" width={`${SIZES.inputSize[0]}rem`} height={`${SIZES.inputSize[1]}rem`} className="mb-4" />
                </div>
            </div>
            <div className="flex flex-row justify-center mt-6 gap-4">
                    <Skeleton variant="rounded" width={`${SIZES.buttonSize[0]}rem`} height={`${SIZES.buttonSize[1]}rem`} className="mb-2" />
                    <Skeleton variant="rounded" width={`${SIZES.buttonSize[0]}rem`} height={`${SIZES.buttonSize[1]}rem`} className="mb-2" />
            </div>
        </div>
    );
}