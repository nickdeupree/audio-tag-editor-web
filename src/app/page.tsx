"use client";
import React from "react";
import Header from "./components/Header";
import Workspace from "./components/Workspace";
import { IconButton, Drawer, Typography, Box, Divider } from "@mui/material";
import HelpIcon from '@mui/icons-material/Help';
import CloseIcon from '@mui/icons-material/Close';


export default function Home() {
  const [open, setOpen] = React.useState(false);

  const toggleDrawer = (verdict: boolean) => {
    setOpen(verdict);
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header/>
      <main className="flex-1 flex justify-center items-start pt-12 px-4 md:px-8 pb-8">
        <Workspace />
      </main>
      <footer className="text-left text-sm py-4 px-2">
        <IconButton aria-label="help" onClick={() => toggleDrawer(true)}>
          <HelpIcon/>
        </IconButton>
        <Drawer open={open} onClose={() => toggleDrawer(false)}>
          <Box sx={{ width: 350, p: 3 }}>
            <IconButton 
              aria-label="close" 
              onClick={() => toggleDrawer(false)}
              sx={{ position: 'absolute', right: 8, top: 8 }}
            >
              <CloseIcon />
            </IconButton>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Help & Disclaimer
            </Typography>
            
            <Typography variant="h6" sx={{ mb: 1, fontSize: '1rem' }}>
              How to Use
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              • Upload audio files or download from YouTube/SoundCloud URLs<br/>
              • Edit metadata tags like title, artist, album, and genre<br/>
              • Download your edited files with updated tags<br/>
            </Typography>

            <Typography variant="h6" sx={{ mb: 1, fontSize: '1rem' }}>
              Supported Formats
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              MP3, WAV, FLAC, M4A, and other common audio formats
            </Typography>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" sx={{ mb: 1, fontSize: '1rem' }}>
              Disclaimer
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Legal Use Only:</strong> This tool is intended for editing metadata of audio files you own or have permission to modify.
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Copyright Respect:</strong> Users are responsible for ensuring they have the right to download and modify any content from YouTube, SoundCloud, or other platforms.
            </Typography>
          </Box>
        </Drawer>
      </footer>
    </div>
  );
}
