"use client";

import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/Button';
import AccountIcon from './AccountIcon';
import Avatar from '@mui/material/Avatar';
import ThemeToggle from './ThemeToggle';
import { useState } from 'react';

export default function Header() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    return (
        <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
            <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Audio Tag Editor
            </Typography>
            <ThemeToggle />
            </Toolbar>
        </AppBar>
        </Box>
    );
}
