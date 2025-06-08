import React from "react";
import { Skeleton } from "@mui/material";
export default function TagEditorSkele() {
    const artSize = 20;
    const inputSize = [15, 2.5] as const;
    const labelSize = [5, 1.25] as const;
    const buttonSize = [10, 3] as const;
    return (
        <div className="flex flex-col">
            <div className="w-full h-full flex flex-row items-start justify-center gap-6">
                <div className="flex flex-col">
                    <Skeleton variant="rounded" width={`${artSize}rem`} height={`${artSize}rem`} />
                </div>
                <div className="flex flex-col">
                    <Skeleton variant="rounded" width={`${labelSize[0]}rem`} height={`${labelSize[1]}rem`} className="mb-2" />
                    <Skeleton variant="rounded" width={`${inputSize[0]}rem`} height={`${inputSize[1]}rem`} className="mb-4" />
                    <Skeleton variant="rounded" width={`${labelSize[0]}rem`} height={`${labelSize[1]}rem`} className="mb-2" />
                    <Skeleton variant="rounded" width={`${inputSize[0]}rem`} height={`${inputSize[1]}rem`} className="mb-4" />
                    <Skeleton variant="rounded" width={`${labelSize[0]}rem`} height={`${labelSize[1]}rem`} className="mb-2" />
                    <Skeleton variant="rounded" width={`${inputSize[0]}rem`} height={`${inputSize[1]}rem`} className="mb-4" />
                    <Skeleton variant="rounded" width={`${labelSize[0]}rem`} height={`${labelSize[1]}rem`} className="mb-2" />
                    <Skeleton variant="rounded" width={`${inputSize[0]}rem`} height={`${inputSize[1]}rem`} />
                </div>
            </div>
            <div className="flex flex-row justify-center mt-6 gap-4">
                    <Skeleton variant="rounded" width={`${buttonSize[0]}rem`} height={`${buttonSize[1]}rem`} className="mb-2" />
                    <Skeleton variant="rounded" width={`${buttonSize[0]}rem`} height={`${buttonSize[1]}rem`} className="mb-2" />
            </div>
        </div>
    );
}
