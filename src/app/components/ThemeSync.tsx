'use client';

import { useEffect } from 'react';
import { useThemeMode } from '../contexts/ThemeContext';

export function ThemeSync() {
  const { actualMode } = useThemeMode();

  useEffect(() => {
    // Update the data-theme attribute on the document element
    document.documentElement.setAttribute('data-theme', actualMode);
    
    // Also update CSS custom properties for compatibility
    const root = document.documentElement;
    if (actualMode === 'dark') {
      root.style.setProperty('--background', '#0a0a0a');
      root.style.setProperty('--foreground', '#ededed');
    } else {
      root.style.setProperty('--background', '#ffffff');
      root.style.setProperty('--foreground', '#111827');
    }
  }, [actualMode]);

  return null; // This component doesn't render anything
}
