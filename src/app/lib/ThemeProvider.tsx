'use client';

import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { createAppTheme } from './theme';
import { useThemeMode } from '../contexts/ThemeContext';

interface AppThemeProviderProps {
  children: React.ReactNode;
}

export function AppThemeProvider({ children }: AppThemeProviderProps) {
  const { actualMode } = useThemeMode();
  const theme = createAppTheme(actualMode);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
