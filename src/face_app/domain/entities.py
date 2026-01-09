"""Domain entities - Core business objects."""
from dataclasses import dataclass
from typing import List


@dataclass
class BoundingBox:
    """Bounding box coordinates for a detected face."""
    top: int
    right: int
    bottom: int
    left: int


@dataclass
class FaceMatch:
    """Result of matching a face against known faces."""
    name: str
    is_known: bool
    distance: float
    
    @property
    def label(self) -> str:
        """Get display label for UI."""
        if self.is_known:
            return self.name
        return "Stranger"


@dataclass
class RecognitionEvent:
    """Event to be persisted to database."""
    name: str
    time: str  # ISO format: YYYY-MM-DD HH:MM:SS


@dataclass
class DetectedFace:
    """A detected face with its encoding and location."""
    box: BoundingBox
    encoding: List[float]
    match: FaceMatch = None
