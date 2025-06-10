import * as React from "react";
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import ToggleButton from '@mui/material/ToggleButton';
import UploadIcon from '@mui/icons-material/Upload';
import YouTubeIcon from '@mui/icons-material/YouTube';
import CloudIcon from '@mui/icons-material/Cloud';
import { useInputStore } from '../store/inputStore';

export default function InputOption() {
    const { selectedOption, setSelectedOption } = useInputStore();

    const handleChange = (event: React.MouseEvent<HTMLElement>, newOption: string) => {
        if (newOption !== null) {
            setSelectedOption(newOption as 'upload' | 'youtube' | 'soundcloud');
        }
    };

    return (
        <div className="input-option flex justify-center my-4">
            <ToggleButtonGroup
                value={selectedOption}
                exclusive
                onChange={handleChange}
                aria-label="Input Option"
                size="small"
            >                
                <ToggleButton value="upload" aria-label="Upload">
                    Your File
                </ToggleButton>                
                <ToggleButton value="youtube" aria-label="YouTube">
                    YouTube
                </ToggleButton>    
                <ToggleButton value="soundcloud" aria-label="SoundCloud">
                    SoundCloud
                </ToggleButton>       
            </ToggleButtonGroup>
        </div>
    );
}