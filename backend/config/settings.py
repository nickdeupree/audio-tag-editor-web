"""
CORS and other configuration settings for the FastAPI app.
"""

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",  # Next.js default port
    "http://127.0.0.1:3000",
    "https://audio-tag-editor-web.vercel.app",  # Vercel deployment
]

CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# Server settings
HOST = "0.0.0.0"
PORT = 8000
