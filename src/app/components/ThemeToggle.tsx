'use client';

import React from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material';
import {
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  SettingsBrightness as SystemModeIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import { useThemeMode } from '../contexts/ThemeContext';

export default function ThemeToggle() {
  const { mode, actualMode, setMode } = useThemeMode();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleModeSelect = (selectedMode: 'light' | 'dark' | 'system') => {
    setMode(selectedMode);
    handleClose();
  };

  const getCurrentIcon = () => {
    if (mode === 'system') {
      return <SystemModeIcon />;
    }
    return actualMode === 'dark' ? <DarkModeIcon /> : <LightModeIcon />;
  };

  const getTooltipText = () => {
    if (mode === 'system') {
      return `System theme (${actualMode})`;
    }
    return `${mode === 'dark' ? 'Dark' : 'Light'} mode`;
  };

  return (
    <>
      <Tooltip title={getTooltipText()}>
        <IconButton
          onClick={handleClick}
          size="small"
          sx={{ ml: 1 }}
          aria-controls={open ? 'theme-menu' : undefined}
          aria-haspopup="true"
          aria-expanded={open ? 'true' : undefined}
        >
          {getCurrentIcon()}
        </IconButton>
      </Tooltip>
      <Menu
        anchorEl={anchorEl}
        id="theme-menu"
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem
          onClick={() => handleModeSelect('light')}
          selected={mode === 'light'}
        >
          <ListItemIcon>
            <LightModeIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Light</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => handleModeSelect('dark')}
          selected={mode === 'dark'}
        >
          <ListItemIcon>
            <DarkModeIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Dark</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => handleModeSelect('system')}
          selected={mode === 'system'}
        >
          <ListItemIcon>
            <SystemModeIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>System</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
}
