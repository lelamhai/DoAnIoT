"""Face Recognition Engine adapter using face_recognition (dlib)."""
from typing import List
import numpy as np
import face_recognition
from face_app.domain.ports import FaceEnginePort
from face_app.domain.entities import BoundingBox
from face_app.config.settings import MODEL


class FRDlibEngine(FaceEnginePort):
    """Adapter for face_recognition library (dlib-based)."""
    
    def __init__(self, model: str = MODEL):
        """
        Initialize face recognition engine.
        
        Args:
            model: "hog" (faster, CPU) or "cnn" (accurate, GPU needed)
        """
        self.model = model
    
    def detect_faces(self, rgb_frame: np.ndarray) -> List[BoundingBox]:
        """
        Detect faces in an RGB frame.
        
        Args:
            rgb_frame: RGB image as numpy array
            
        Returns:
            List of BoundingBox objects
        """
        # face_recognition returns (top, right, bottom, left)
        locations = face_recognition.face_locations(rgb_frame, model=self.model)
        
        return [
            BoundingBox(top=top, right=right, bottom=bottom, left=left)
            for top, right, bottom, left in locations
        ]
    
    def encode_faces(self, rgb_frame: np.ndarray, boxes: List[BoundingBox]) -> List[np.ndarray]:
        """
        Generate face encodings for detected faces.
        
        Args:
            rgb_frame: RGB image as numpy array
            boxes: List of BoundingBox for detected faces
            
        Returns:
            List of 128-dimensional face encodings
        """
        # Convert BoundingBox to face_recognition format: [(top, right, bottom, left), ...]
        locations = [(box.top, box.right, box.bottom, box.left) for box in boxes]
        
        # Generate encodings
        encodings = face_recognition.face_encodings(rgb_frame, known_face_locations=locations)
        
        return encodings
    
    def compute_distances(self, known_encodings: List[np.ndarray], probe_encoding: np.ndarray) -> List[float]:
        """
        Compute distances between known encodings and a probe encoding.
        
        Args:
            known_encodings: List of known face encodings
            probe_encoding: Encoding of the face to match
            
        Returns:
            List of distances (lower = more similar)
        """
        if not known_encodings:
            return []
        
        # face_recognition.face_distance returns numpy array
        distances = face_recognition.face_distance(known_encodings, probe_encoding)
        
        return distances.tolist()
