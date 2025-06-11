"""
CORS and other configuration settings for the FastAPI app.
"""
import os

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",  # Next.js default port
    "http://127.0.0.1:3000",
    "https://audio-tag-editor-web.vercel.app",  # Vercel production deployment
    "https://audio-tag-editor-web-git-main-nickdeuprees-projects.vercel.app",  # Vercel git deployment
    "https://audio-tag-editor-web-nickdeuprees-projects.vercel.app",  # Vercel project deployment
]

# Add additional CORS origins from environment variable if set
additional_origins = os.getenv("ADDITIONAL_CORS_ORIGINS")
if additional_origins:
    CORS_ORIGINS.extend(additional_origins.split(","))

CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# Server settings
HOST = "0.0.0.0"
PORT = 8000
