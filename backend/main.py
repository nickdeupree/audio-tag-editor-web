"""
Main FastAPI application setup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, health
from config.settings import (
    CORS_ORIGINS, 
    CORS_CREDENTIALS, 
    CORS_METHODS, 
    CORS_HEADERS
)

app = FastAPI(
    title="Audio Tag Editor Backend",
    description="A FastAPI backend for handling audio file uploads and tag editing",
    version="1.0.0"
)

# Add CORS middleware to allow requests from your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(upload.router, tags=["upload"])

if __name__ == "__main__":
    import uvicorn
    import os
    
    print("Starting Audio Tag Editor Backend...")
    port = int(os.environ.get("PORT", 8000))
    print(f"Server will be available at: http://0.0.0.0:{port}")
    print(f"API docs will be available at: http://0.0.0.0:{port}/docs")
    print("Make sure your frontend is configured to use this backend URL")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)
