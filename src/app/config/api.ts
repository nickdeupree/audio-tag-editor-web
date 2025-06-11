const getBaseUrl = () => {
  // For Next.js API routes, always use relative paths
  return '';
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
  // All endpoints are now Next.js API routes, so just return the endpoint
  return endpoint;
};
