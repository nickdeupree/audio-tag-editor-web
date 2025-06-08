"""
Health check and other general API routes.
"""

from fastapi import APIRouter
from models.responses import HealthResponse

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(message="Audio Tag Editor Backend is running!")
