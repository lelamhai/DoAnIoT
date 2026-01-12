"""Use case for recognizing faces in a frame."""
from datetime import datetime, timedelta
from typing import Dict, Optional
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
        cooldown_seconds: int = COOLDOWN_SECONDS,
        stranger_monitor=None,  # Optional StrangerMonitor instance
        known_person_monitors: dict = None  # Dict of PersonDetectionMonitor per known person
    ):
        """
        Initialize use case.
        
        Args:
            face_engine: Face detection/encoding engine
            load_known_usecase: Use case for loading known faces
            recognition_repo: Repository for persisting events
            match_policy: Policy for matching faces
            cooldown_seconds: Minimum seconds between logging same person
            stranger_monitor: Optional stranger detection monitor
            known_person_monitors: Optional dict of {name: PersonDetectionMonitor}
        """
        self.face_engine = face_engine
        self.load_known_usecase = load_known_usecase
        self.recognition_repo = recognition_repo
        self.match_policy = match_policy
        self.cooldown_seconds = cooldown_seconds
        self.stranger_monitor = stranger_monitor
        self.known_person_monitors = known_person_monitors or {}
        
        # Cache for last recognition time (in-memory)
        self._last_recognition: Dict[str, datetime] = {}
    
    def execute(self, frame_bgr: np.ndarray, active: bool = True) -> RecognitionResult:
        """
        Recognize faces in a frame.
        
        Args:
            frame_bgr: BGR frame from camera
            active: Control database logging and email (True = enable, False = disable)
            
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
            
            # Persist to database (with cooldown) - chỉ khi active=True
            self._persist_if_needed(match.label, active=active)
            
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
    
    def _persist_if_needed(self, name: str, active: bool = True) -> None:
        """
        Persist recognition event using detection monitors.
        
        Args:
            name: Person name or "Stranger"
            active: If False, skip all DB logging and email sending
        """
        # Nếu active=False, không ghi DB và không gửi email
        if not active:
            return
        # Track stranger detection - only log when alert triggered
        if name == "Stranger" and self.stranger_monitor:
            self.stranger_monitor.record_detection(is_stranger=True, name=name)
            return  # Don't log to DB here, let monitor callback handle it
        
        # Track known person detection - only log when threshold reached
        if name in self.known_person_monitors:
            monitor = self.known_person_monitors[name]
            monitor.record_detection(detected_name=name)
            return  # Don't log to DB here, let monitor callback handle it
        
        # Fallback: if no monitor exists, use cooldown-based logging
        now = datetime.now()
        if name in self._last_recognition:
            time_since_last = now - self._last_recognition[name]
            if time_since_last.total_seconds() < self.cooldown_seconds:
                return
        
        self._last_recognition[name] = now
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self.recognition_repo.insert_event(name, time_str)
        print(f"📝 Logged: {name} at {time_str}")
