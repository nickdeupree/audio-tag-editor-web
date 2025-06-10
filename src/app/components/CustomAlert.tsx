import React, { useEffect } from 'react';
import Alert from '@mui/material/Alert';

interface CustomAlertProps {
    message: string;
    severity: 'error' | 'warning' | 'info' | 'success';
    autoHideDuration?: number;
    onClose?: () => void;
}

export default function CustomAlert({
    message, 
    severity, 
    autoHideDuration = 3000, 
    onClose
}: CustomAlertProps) {
    useEffect(() => {
        if (autoHideDuration && onClose) {
            const timer = setTimeout(() => {
                onClose();
            }, autoHideDuration);

            return () => clearTimeout(timer);
        }
    }, [autoHideDuration, onClose]);

    return (
        <Alert 
            severity={severity} 
            sx={{ width: '100%' }}
            onClose={onClose}
        >
            {message}
        </Alert>
    );
}