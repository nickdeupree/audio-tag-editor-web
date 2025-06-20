/**
 * API Configuration for Audio Tag Editor
 * 
 * This configuration handles Vercel's 4.5MB serverless function payload limit
 * by using a hybrid approach:
 * 
 * 1. File uploads go directly to the backend (bypasses Vercel limits)
 * 2. Other operations use Next.js API routes (better error handling)
 */

const getDirectBackendUrl = () => {
  // For direct backend calls (file uploads), use the full backend URL
  if (process.env.NODE_ENV === 'production') {
    return process.env.NEXT_PUBLIC_API_URL || 'https://audio-tag-editor-web.onrender.com';
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

export const API_CONFIG = {
  BASE_URL: '',
  DIRECT_BACKEND_URL: getDirectBackendUrl(),
  ENDPOINTS: {
    UPLOAD: '/upload/',
    UPDATE_TAGS: '/api/upload/update-tags',
    UPDATE_WORKSPACE_TAGS: '/api/upload/update-workspace-tags',
    COVER_ART: '/api/upload/cover-art',
    DOWNLOAD_YOUTUBE: '/api/upload/download/youtube',
    DOWNLOAD_SOUNDCLOUD: '/api/upload/download/soundcloud',
    DOWNLOAD_FILE: '/api/upload/download',
    DOWNLOAD_BY_FILENAME: '/api/upload/download/by-filename', // New filename-based download
    DOWNLOAD_LATEST: '/api/upload/download-latest',
    DOWNLOAD_ALL: '/api/upload/download-all',
    CLEAR_CACHE: '/api/upload/clear-cache',
    FILES_ALL: '/api/upload/files/all',
  }
};

export const getApiUrl = (endpoint: string) => {
  // For file uploads, use direct backend URL to bypass Vercel payload limits
  if (endpoint === API_CONFIG.ENDPOINTS.UPLOAD) {
    return `${API_CONFIG.DIRECT_BACKEND_URL}${endpoint}`;
  }
  // For other operations, use Next.js API routes
  return endpoint;
};
