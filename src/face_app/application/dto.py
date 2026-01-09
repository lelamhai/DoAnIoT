"""Data Transfer Objects for application layer."""
from dataclasses import dataclass
from typing import List
from face_app.domain.entities import BoundingBox, FaceMatch


@dataclass
class RecognitionResult:
    """Result of recognizing faces in a frame."""
    faces: List['FaceRecognitionDTO']
    processed: bool = True
    

@dataclass
class FaceRecognitionDTO:
    """DTO for a recognized face (for UI presentation)."""
    box: BoundingBox
    name: str
    is_known: bool
    distance: float
    
    @property
    def label(self) -> str:
        """Get display label."""
        return self.name
    
    @property
    def color(self) -> tuple:
        """Get color based on known/unknown."""
        from face_app.config.settings import BBOX_COLOR_KNOWN, BBOX_COLOR_UNKNOWN
        return BBOX_COLOR_KNOWN if self.is_known else BBOX_COLOR_UNKNOWN
