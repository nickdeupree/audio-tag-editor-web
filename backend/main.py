#!/usr/bin/env python3
"""
Audio Tag Editor Backend
A FastAPI backend for handling audio file uploads and tag editing.
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting Audio Tag Editor Backend...")
    print("Server will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Make sure your Next.js app is running on http://localhost:3000")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
