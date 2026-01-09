"""Domain ports - Interfaces for external dependencies."""
from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
from .entities import BoundingBox


class FaceEnginePort(ABC):
    """Interface for face detection and encoding engine."""
    
    @abstractmethod
    def detect_faces(self, rgb_frame: np.ndarray) -> List[BoundingBox]:
        """Detect faces in an RGB frame and return bounding boxes."""
        pass
    
    @abstractmethod
    def encode_faces(self, rgb_frame: np.ndarray, boxes: List[BoundingBox]) -> List[np.ndarray]:
        """Generate face encodings for detected faces."""
        pass
    
    @abstractmethod
    def compute_distances(self, known_encodings: List[np.ndarray], probe_encoding: np.ndarray) -> List[float]:
        """Compute distances between known encodings and a probe encoding."""
        pass


class KnownFaceRepoPort(ABC):
    """Interface for loading known faces dataset."""
    
    @abstractmethod
    def load_known_faces(self) -> Tuple[List[np.ndarray], List[str]]:
        """
        Load known faces from dataset.
        Returns: (encodings, names)
        """
        pass


class RecognitionRepoPort(ABC):
    """Interface for persisting recognition events."""
    
    @abstractmethod
    def insert_event(self, name: str, time: str) -> None:
        """Insert a recognition event (name + time)."""
        pass
    
    @abstractmethod
    def get_last_event_time(self, name: str) -> str | None:
        """Get the last time this person was recognized (for cooldown)."""
        pass


class CameraPort(ABC):
    """Interface for camera capture."""
    
    @abstractmethod
    def read(self) -> Tuple[bool, np.ndarray]:
        """Read a frame from camera. Returns (success, frame_bgr)."""
        pass
    
    @abstractmethod
    def release(self) -> None:
        """Release camera resources."""
        pass
    
    @abstractmethod
    def is_opened(self) -> bool:
        """Check if camera is opened."""
        pass
