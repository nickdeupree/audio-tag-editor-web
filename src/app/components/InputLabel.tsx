import React from 'react';
import { Typography } from '@mui/material';
export default function InputLabel({ label, height, width }: { label: string; height: number; width: number; }) {
    return (
        <Typography
            variant="body1"
            component="label"
            style={{ color: 'var(--color-text)', height, width }}
            className="mb-2"
        >
            {label}
        </Typography>
    );
}