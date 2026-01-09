"""Use case for recognizing faces in a frame."""
from datetime import datetime, timedelta
from typing import Dict
import numpy as np
import cv2
from face_app.domain.ports import FaceEnginePort, RecognitionRepoPort
from face_app.domain.policies import MatchPolicy
from face_app.application.dto import RecognitionResult, FaceRecognitionDTO
from face_app.application.usecases.load_known_faces import LoadKnownFacesUseCase
from face_app.config.settings import COOLDOWN_SECONDS, FRAME_WIDTH


class RecognizeFrameUseCase:
    """Recognize faces in a video frame."""
    
    def __init__(
        self,
        face_engine: FaceEnginePort,
        load_known_usecase: LoadKnownFacesUseCase,
        recognition_repo: RecognitionRepoPort,
        match_policy: MatchPolicy,
        cooldown_seconds: int = COOLDOWN_SECONDS
    ):
        """
        Initialize use case.
        
        Args:
            face_engine: Face detection/encoding engine
            load_known_usecase: Use case for loading known faces
            recognition_repo: Repository for persisting events
            match_policy: Policy for matching faces
            cooldown_seconds: Minimum seconds between logging same person
        """
        self.face_engine = face_engine
        self.load_known_usecase = load_known_usecase
        self.recognition_repo = recognition_repo
        self.match_policy = match_policy
        self.cooldown_seconds = cooldown_seconds
        
        # Cache for last recognition time (in-memory)
        self._last_recognition: Dict[str, datetime] = {}
    
    def execute(self, frame_bgr: np.ndarray) -> RecognitionResult:
        """
        Recognize faces in a frame.
        
        Args:
            frame_bgr: BGR frame from camera
            
        Returns:
            RecognitionResult with detected faces
        """
        # Preprocess: resize for faster processing
        height, width = frame_bgr.shape[:2]
        scale = FRAME_WIDTH / width
        small_frame = cv2.resize(frame_bgr, (0, 0), fx=scale, fy=scale)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        boxes = self.face_engine.detect_faces(rgb_frame)
        
        if not boxes:
            return RecognitionResult(faces=[])
        
        # Encode faces
        encodings = self.face_engine.encode_faces(rgb_frame, boxes)
        
        # Get known faces
        known_encodings = self.load_known_usecase.known_encodings
        known_names = self.load_known_usecase.known_names
        
        # Match each detected face
        results = []
        
        for box, encoding in zip(boxes, encodings):
            # Scale box back to original frame size
            scaled_box = self._scale_box(box, 1/scale)
            
            # Compute distances
            distances = self.face_engine.compute_distances(known_encodings, encoding)
            
            # Match using policy
            match = self.match_policy.match(known_encodings, known_names, encoding, distances)
            
            # Persist to database (with cooldown)
            self._persist_if_needed(match.label)
            
            # Create DTO
            face_dto = FaceRecognitionDTO(
                box=scaled_box,
                name=match.label,
                is_known=match.is_known,
                distance=match.distance
            )
            results.append(face_dto)
        
        return RecognitionResult(faces=results)
    
    def _scale_box(self, box, scale: float):
        """Scale bounding box coordinates."""
        from face_app.domain.entities import BoundingBox
        return BoundingBox(
            top=int(box.top * scale),
            right=int(box.right * scale),
            bottom=int(box.bottom * scale),
            left=int(box.left * scale)
        )
    
    def _persist_if_needed(self, name: str) -> None:
        """
        Persist recognition event with cooldown.
        
        Args:
            name: Person name or "Stranger"
        """
        now = datetime.now()
        
        # Check cooldown
        if name in self._last_recognition:
            time_since_last = now - self._last_recognition[name]
            if time_since_last.total_seconds() < self.cooldown_seconds:
                # Still in cooldown period
                return
        
        # Update last recognition time
        self._last_recognition[name] = now
        
        # Persist to database
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self.recognition_repo.insert_event(name, time_str)
        
        # Log to console
        print(f"📝 Logged: {name} at {time_str}")
