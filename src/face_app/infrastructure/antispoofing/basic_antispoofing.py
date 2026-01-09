"""Basic anti-spoofing / liveness detection."""
import cv2
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class LivenessResult:
    """Result of liveness detection."""
    is_live: bool
    score: float
    method: str
    details: dict


class BasicAntiSpoofing:
    """Basic anti-spoofing using simple heuristics."""
    
    def __init__(
        self,
        motion_threshold: float = 2.0,  # Minimum motion score
        texture_threshold: float = 10.0,  # Minimum texture variance
        enable_motion: bool = True,
        enable_texture: bool = True
    ):
        """
        Initialize anti-spoofing detector.
        
        Args:
            motion_threshold: Minimum motion between frames to be considered live
            texture_threshold: Minimum texture variance (higher = more texture)
            enable_motion: Enable motion-based detection
            enable_texture: Enable texture-based detection
        """
        self.motion_threshold = motion_threshold
        self.texture_threshold = texture_threshold
        self.enable_motion = enable_motion
        self.enable_texture = enable_texture
        
        self.prev_gray = None
    
    def check_liveness(
        self,
        frame: np.ndarray,
        face_bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> LivenessResult:
        """
        Check if face is live (not a photo/video).
        
        Args:
            frame: BGR frame
            face_bbox: Optional (x, y, w, h) to focus on face region
            
        Returns:
            LivenessResult with score and details
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Extract face region if provided
        if face_bbox:
            x, y, w, h = face_bbox
            roi = gray[y:y+h, x:x+w]
        else:
            roi = gray
        
        scores = {}
        is_live = True
        
        # 1. Texture analysis (photos have less texture variance)
        if self.enable_texture:
            texture_score = self._compute_texture_score(roi)
            scores['texture'] = texture_score
            
            if texture_score < self.texture_threshold:
                is_live = False
        
        # 2. Motion detection (photos don't move naturally)
        if self.enable_motion and self.prev_gray is not None:
            motion_score = self._compute_motion_score(gray, self.prev_gray, face_bbox)
            scores['motion'] = motion_score
            
            # Note: Too little OR too much motion can indicate spoofing
            if motion_score < self.motion_threshold:
                is_live = False
        
        self.prev_gray = gray.copy()
        
        # Combined score
        combined_score = np.mean(list(scores.values())) if scores else 0.0
        
        return LivenessResult(
            is_live=is_live,
            score=combined_score,
            method='basic_heuristics',
            details=scores
        )
    
    def _compute_texture_score(self, roi: np.ndarray) -> float:
        """
        Compute texture richness score using Laplacian variance.
        Real faces have more texture than printed photos.
        """
        laplacian = cv2.Laplacian(roi, cv2.CV_64F)
        variance = laplacian.var()
        return float(variance)
    
    def _compute_motion_score(
        self,
        current: np.ndarray,
        previous: np.ndarray,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> float:
        """
        Compute motion score between frames.
        Real faces have subtle natural motion.
        """
        # Optical flow or simple frame difference
        if bbox:
            x, y, w, h = bbox
            current_roi = current[y:y+h, x:x+w]
            prev_roi = previous[y:y+h, x:x+w]
        else:
            current_roi = current
            prev_roi = previous
        
        # Ensure same size
        if current_roi.shape != prev_roi.shape:
            return 0.0
        
        # Frame difference
        diff = cv2.absdiff(current_roi, prev_roi)
        motion_score = float(np.mean(diff))
        
        return motion_score
    
    def reset(self):
        """Reset state (e.g., when new person detected)."""
        self.prev_gray = None


class BlinkDetection:
    """Eye blink detection for liveness (more advanced)."""
    
    def __init__(self, blink_threshold: int = 3, frame_window: int = 30):
        """
        Initialize blink detector.
        
        Args:
            blink_threshold: Minimum blinks required in window
            frame_window: Number of frames to check for blinks
        """
        self.blink_threshold = blink_threshold
        self.frame_window = frame_window
        self.eye_states = []  # History of eye open/closed states
    
    def detect_blink(self, landmarks: np.ndarray) -> bool:
        """
        Detect eye blink from facial landmarks.
        
        Args:
            landmarks: Facial landmarks (68 or 106 points)
            
        Returns:
            True if blink detected
        """
        # This is simplified - real implementation needs proper landmark indices
        # For 68-point landmarks: eyes are points 36-47
        # For InsightFace 106-point: different indices
        
        # Placeholder - would calculate Eye Aspect Ratio (EAR)
        # EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        # If EAR < threshold, eye is closed
        
        return False  # Simplified for MVP
    
    def is_live(self) -> bool:
        """Check if enough blinks detected in window."""
        if len(self.eye_states) < self.frame_window:
            return False
        
        recent_blinks = sum(self.eye_states[-self.frame_window:])
        return recent_blinks >= self.blink_threshold
    
    def reset(self):
        """Reset blink history."""
        self.eye_states.clear()


def check_face_quality(frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> dict:
    """
    Check face quality metrics.
    
    Args:
        frame: BGR frame
        bbox: (x, y, w, h) bounding box
        
    Returns:
        Dict with quality metrics
    """
    x, y, w, h = bbox
    face_roi = frame[y:y+h, x:x+w]
    
    # Brightness
    gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    
    # Sharpness (Laplacian variance)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = laplacian.var()
    
    # Size (larger faces = better quality)
    size = w * h
    
    return {
        'brightness': float(brightness),
        'sharpness': float(sharpness),
        'size': size,
        'good_quality': brightness > 50 and sharpness > 100 and size > 10000
    }
