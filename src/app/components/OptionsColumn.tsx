import React from 'react';
import UploadFile from './UploadFile';
import { Upload } from '@mui/icons-material';
import YouTubeUrl from './YouTubeUrl';
import SoundCloudUrl from './SoundCloudUrl';
import { useInputStore } from '../store/inputStore';

export default function OptionsColumn() {
    const { selectedOption } = useInputStore();

    const renderSelectedComponent = () => {
        switch (selectedOption) {
            case 'upload':
                return <UploadFile />;
            case 'youtube':
                return <YouTubeUrl />;
            case 'soundcloud':
                return <SoundCloudUrl />;
            default:
                return <UploadFile />;
        }
    };

    return (
        <div>
            {renderSelectedComponent()}
        </div>
    );
}