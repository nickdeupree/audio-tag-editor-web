# Vercel Payload Limit Workaround - Complete Implementation

This project successfully handles Vercel's 4.5MB serverless function payload limit using a hybrid architecture.

## Problem Solved

**Before**: `Upload failed: Request Entity Too Large - FUNCTION_PAYLOAD_TOO_LARGE`
**After**: Large audio files upload directly to backend, bypassing Vercel limits entirely.

## Architecture Overview

### 🎯 Direct Backend Calls (Large Payloads)
- **Route**: `/upload/` 
- **Method**: Direct API calls to Render backend
- **Purpose**: Bypass Vercel's 4.5MB payload limit
- **CORS**: Enabled on backend for cross-origin requests

### 🔄 Next.js API Routes (Small Payloads)
- **Routes**: `/api/upload/*`
- **Method**: Proxied through Next.js serverless functions
- **Purpose**: Better error handling, consistent API interface, no CORS issues

## Implementation Details

### Frontend API Configuration (`src/app/config/api.ts`)

```typescript
// File uploads go directly to backend
if (endpoint === API_CONFIG.ENDPOINTS.UPLOAD) {
  return `${API_CONFIG.DIRECT_BACKEND_URL}${endpoint}`;
}
// Other operations use Next.js API routes
return endpoint;
```

### Backend CORS Configuration (`backend/config/settings.py`)

```python
CORS_ORIGINS = [
  "http://localhost:3000",  # Development
  "https://audio-tag-editor-web.vercel.app",  # Production
  "https://audio-tag-editor-web-git-main-nickdeuprees-projects.vercel.app",
  "https://audio-tag-editor-web-nickdeuprees-projects.vercel.app",
]
```

## Endpoint Routing

| Endpoint | Method | Route Type | Purpose |
|----------|--------|------------|---------|
| `/upload/` | Direct Backend | File Upload | Bypass 4.5MB limit |
| `/api/upload/update-tags` | Next.js API | Metadata Update | Error handling |
| `/api/upload/download/youtube` | Next.js API | YouTube Download | Proxy to backend |
| `/api/upload/download/soundcloud` | Next.js API | SoundCloud Download | Proxy to backend |
| `/api/upload/cover-art` | Next.js API | Cover Art Upload | Error handling |
| `/api/upload/download/*` | Next.js API | File Downloads | Stream files |

## Environment Variables

### Vercel Deployment Settings
```bash
NEXT_PUBLIC_API_URL=https://audio-tag-editor-web.onrender.com
PYTHON_BACKEND_URL=https://audio-tag-editor-web.onrender.com
```

### Local Development (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
PYTHON_BACKEND_URL=http://localhost:8000
```

## File Size Limits

- **Vercel Serverless Functions**: 4.5MB (bypassed for uploads)
- **Render.com**: 100MB+ (handles actual file processing)
- **Audio Files**: No practical limit via direct upload
- **Cover Art**: Embedded as base64 in metadata (compressed)

## Testing

Build test confirms all routes compile correctly:
```bash
npm run build
# ✓ Compiled successfully
# ✓ All API routes generated
```

Runtime test confirms correct routing:
```bash
UPLOAD endpoint: http://localhost:8000/upload/        # Direct backend
UPDATE_TAGS endpoint: /api/upload/update-tags         # Next.js API route
DOWNLOAD_YOUTUBE endpoint: /api/upload/download/youtube # Next.js API route
```

## Benefits

1. **No Size Limits**: Audio files can be any size supported by Render
2. **Better UX**: Users no longer see payload size errors
3. **CORS Free**: Direct uploads work without CORS issues
4. **Error Handling**: Non-upload operations still get Next.js error handling
5. **Performance**: Files stream directly to backend without proxy overhead

## Deployment Notes

When deploying to Vercel, ensure these environment variables are set in the Vercel dashboard, not just in `.env.production` files, as Vercel needs them at build time.
