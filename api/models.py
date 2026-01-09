"""Pydantic models for API."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RecognitionEventResponse(BaseModel):
    """Response model for recognition event."""
    id: int
    name: str
    time: str


class RecognitionStatsResponse(BaseModel):
    """Response model for statistics."""
    total_events: int
    unique_people: int
    today_events: int
    most_frequent_person: Optional[str] = None
    most_frequent_count: Optional[int] = None


class RecognizeRequest(BaseModel):
    """Request model for /recognize endpoint."""
    image_base64: str  # Base64 encoded image


class FaceDetectionResponse(BaseModel):
    """Response for a single detected face."""
    name: str
    is_known: bool
    distance: float
    box: dict  # {top, right, bottom, left}


class RecognizeResponse(BaseModel):
    """Response model for /recognize endpoint."""
    success: bool
    faces: List[FaceDetectionResponse]
    processed_at: str
    message: Optional[str] = None
