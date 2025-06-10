export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  ENDPOINTS: {
    UPLOAD: '/upload/',
    UPDATE_TAGS: '/upload/update-tags',
    DOWNLOAD_YOUTUBE: '/upload/download/youtube',
    DOWNLOAD_SOUNDCLOUD: '/upload/download/soundcloud',
    DOWNLOAD_FILE: '/upload/download',
    DOWNLOAD_LATEST: '/upload/download-latest',
    DOWNLOAD_ALL: '/upload/download-all',
  }
};

export const getApiUrl = (endpoint: string) => `${API_CONFIG.BASE_URL}${endpoint}`;
