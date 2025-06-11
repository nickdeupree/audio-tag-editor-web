const getBaseUrl = () => {
  // In production, use the production URL, otherwise fall back to localhost
  if (process.env.NODE_ENV === 'production') {
    return process.env.NEXT_PUBLIC_API_URL || 'https://audio-tag-editor-web.onrender.com';
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

export const API_CONFIG = {
  BASE_URL: getBaseUrl(),
  ENDPOINTS: {
    UPLOAD: '/api/upload',
    UPDATE_TAGS: '/api/upload/update-tags',
    DOWNLOAD_YOUTUBE: '/api/upload/download/youtube',
    DOWNLOAD_SOUNDCLOUD: '/api/upload/download/soundcloud',
    DOWNLOAD_FILE: '/api/upload/download',
    DOWNLOAD_LATEST: '/api/upload/download-latest',
    DOWNLOAD_ALL: '/api/upload/download-all',
  }
};

export const getApiUrl = (endpoint: string) => {
  // For Next.js API routes, use relative URLs
  if (endpoint.startsWith('/api/')) {
    return endpoint;
  }
  // For direct backend calls (download endpoints), use the full URL
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
