# Audio Tag Editor Backend

A modular FastAPI backend for handling audio file uploads and tag editing.

## Project Structure

```
backend/
├── main.py                 # Entry point for the backend server
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── app/
│   ├── __init__.py
│   └── main.py            # FastAPI app configuration
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration settings (CORS, server settings)
├── models/
│   ├── __init__.py
│   └── responses.py       # Pydantic models for API responses
├── routers/
│   ├── __init__.py
│   ├── health.py          # Health check endpoints
│   └── upload.py          # File upload endpoints
└── services/
    ├── __init__.py
    └── file_service.py     # Business logic for file operations
```

## Setup and Running

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. **Option 1: Using the startup script (Recommended)**
   ```powershell
   .\start.ps1
   ```
   This script will automatically:
   - Create a virtual environment if it doesn't exist
   - Activate the virtual environment
   - Install dependencies
   - Start the server

3. **Option 2: Manual setup**
   - Create and activate virtual environment:
     ```bash
     python -m venv venv
     venv\Scripts\Activate.ps1  # On Windows PowerShell
     # or
     venv\Scripts\activate      # On Windows Command Prompt
     # or
     source venv/bin/activate   # On Linux/Mac
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the backend server:
     ```bash
     python main.py
     ```

The server will be available at:
- Main server: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

- `GET /` - Health check endpoint
- `POST /upload` - Upload audio files

## Development

The backend is organized into modules for better maintainability:

- **app/**: FastAPI application setup and configuration
- **config/**: Configuration settings and constants
- **models/**: Pydantic models for request/response validation
- **routers/**: API route definitions organized by functionality
- **services/**: Business logic and service layer functions
