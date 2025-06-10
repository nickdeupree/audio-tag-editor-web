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
    port = int(os.environ.get("PORT", 8000))
    print(f"Server will be available at: http://0.0.0.0:{port}")
    print(f"API docs will be available at: http://0.0.0.0:{port}/docs")
    print("Make sure your frontend is configured to use this backend URL")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)
