"""Domain policies - Business rules and decision logic."""
from typing import List
import numpy as np
from .entities import FaceMatch


class MatchPolicy:
    """Policy for matching detected faces against known faces."""
    
    def __init__(self, tolerance: float = 0.5):
        """
        Initialize match policy.
        
        Args:
            tolerance: Maximum distance to consider a match (0.4-0.6 recommended).
                      Lower = stricter matching.
        """
        self.tolerance = tolerance
    
    def match(
        self, 
        known_encodings: List[np.ndarray], 
        known_names: List[str],
        probe_encoding: np.ndarray,
        distances: List[float]
    ) -> FaceMatch:
        """
        Match a probe face against known faces.
        
        Args:
            known_encodings: List of known face encodings
            known_names: List of names corresponding to encodings
            probe_encoding: Encoding of the face to match
            distances: Precomputed distances
            
        Returns:
            FaceMatch with name, is_known, and distance
        """
        if not distances:
            return FaceMatch(name="Unknown", is_known=False, distance=1.0)
        
        # Find best match
        min_distance_idx = int(np.argmin(distances))
        min_distance = distances[min_distance_idx]
        
        # Check if within tolerance
        if min_distance < self.tolerance:
            return FaceMatch(
                name=known_names[min_distance_idx],
                is_known=True,
                distance=min_distance
            )
        else:
            return FaceMatch(
                name="Stranger",
                is_known=False,
                distance=min_distance
            )
