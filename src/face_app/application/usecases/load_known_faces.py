"""Use case for loading known faces from dataset."""
from typing import List, Tuple
import numpy as np
from face_app.domain.ports import KnownFaceRepoPort


class LoadKnownFacesUseCase:
    """Load known faces from dataset."""
    
    def __init__(self, known_repo: KnownFaceRepoPort):
        """
        Initialize use case.
        
        Args:
            known_repo: Repository for loading known faces
        """
        self.known_repo = known_repo
        self._known_encodings: List[np.ndarray] = []
        self._known_names: List[str] = []
        self._loaded = False
    
    def execute(self) -> Tuple[List[np.ndarray], List[str]]:
        """
        Load and cache known faces.
        
        Returns:
            (encodings, names)
        """
        if not self._loaded:
            self._known_encodings, self._known_names = self.known_repo.load_known_faces()
            self._loaded = True
        
        return self._known_encodings, self._known_names
    
    def reload(self) -> Tuple[List[np.ndarray], List[str]]:
        """Force reload of known faces (for hot reload feature)."""
        self._loaded = False
        return self.execute()
    
    @property
    def known_encodings(self) -> List[np.ndarray]:
        """Get cached encodings."""
        if not self._loaded:
            self.execute()
        return self._known_encodings
    
    @property
    def known_names(self) -> List[str]:
        """Get cached names."""
        if not self._loaded:
            self.execute()
        return self._known_names
