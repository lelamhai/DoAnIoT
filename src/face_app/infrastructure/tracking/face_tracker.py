"""Face tracking to reduce computation - track faces between frames."""
import cv2
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from face_app.domain.entities import BoundingBox, FaceMatch


@dataclass
class TrackedFace:
    """A tracked face across frames."""
    track_id: int
    bbox: BoundingBox
    match: FaceMatch
    frames_since_update: int = 0
    total_frames: int = 1


class FaceTracker:
    """Track faces across frames to reduce detection/recognition compute."""
    
    def __init__(
        self, 
        detect_interval: int = 5,  # Detect every N frames
        max_disappeared: int = 10,  # Remove track after N frames
        iou_threshold: float = 0.3  # IoU threshold for matching
    ):
        """
        Initialize face tracker.
        
        Args:
            detect_interval: Run full detection every N frames (track in between)
            max_disappeared: Remove track if not updated for N frames
            iou_threshold: IoU threshold for bbox matching
        """
        self.detect_interval = detect_interval
        self.max_disappeared = max_disappeared
        self.iou_threshold = iou_threshold
        
        self.tracks: Dict[int, TrackedFace] = {}
        self.next_track_id = 0
        self.frame_count = 0
        
        # OpenCV tracker
        self.cv_trackers: Dict[int, cv2.Tracker] = {}
    
    def should_detect(self) -> bool:
        """Check if we should run full detection this frame."""
        return self.frame_count % self.detect_interval == 0
    
    def update_tracks(
        self, 
        frame: np.ndarray,
        boxes: Optional[List[BoundingBox]] = None,
        matches: Optional[List[FaceMatch]] = None
    ) -> List[TrackedFace]:
        """
        Update tracks with new detections or track existing faces.
        
        Args:
            frame: BGR frame
            boxes: New detected boxes (if detection frame)
            matches: Face matches corresponding to boxes
            
        Returns:
            List of tracked faces
        """
        self.frame_count += 1
        
        if self.should_detect() and boxes is not None:
            # Full detection frame - update/create tracks
            return self._update_with_detections(frame, boxes, matches or [])
        else:
            # Tracking frame - update positions using tracker
            return self._update_with_tracking(frame)
    
    def _update_with_detections(
        self,
        frame: np.ndarray,
        boxes: List[BoundingBox],
        matches: List[FaceMatch]
    ) -> List[TrackedFace]:
        """Update tracks with new detections."""
        # Match new detections to existing tracks
        matched_tracks = set()
        new_tracks = []
        
        for box, match in zip(boxes, matches):
            # Find best matching track
            best_track_id = None
            best_iou = 0.0
            
            for track_id, track in self.tracks.items():
                iou = self._compute_iou(box, track.bbox)
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id
            
            if best_track_id is not None:
                # Update existing track
                track = self.tracks[best_track_id]
                track.bbox = box
                track.match = match
                track.frames_since_update = 0
                track.total_frames += 1
                matched_tracks.add(best_track_id)
                
                # Reinitialize CV tracker
                self._init_cv_tracker(frame, best_track_id, box)
            else:
                # Create new track
                track = TrackedFace(
                    track_id=self.next_track_id,
                    bbox=box,
                    match=match,
                    frames_since_update=0,
                    total_frames=1
                )
                self.tracks[self.next_track_id] = track
                self._init_cv_tracker(frame, self.next_track_id, box)
                self.next_track_id += 1
        
        # Remove old tracks
        tracks_to_remove = []
        for track_id in self.tracks:
            if track_id not in matched_tracks:
                self.tracks[track_id].frames_since_update += 1
                if self.tracks[track_id].frames_since_update > self.max_disappeared:
                    tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
            if track_id in self.cv_trackers:
                del self.cv_trackers[track_id]
        
        return list(self.tracks.values())
    
    def _update_with_tracking(self, frame: np.ndarray) -> List[TrackedFace]:
        """Update tracks using OpenCV tracker."""
        tracks_to_remove = []
        
        for track_id, tracker in list(self.cv_trackers.items()):
            success, bbox = tracker.update(frame)
            
            if success:
                # Update track bbox
                x, y, w, h = [int(v) for v in bbox]
                self.tracks[track_id].bbox = BoundingBox(
                    top=y,
                    right=x + w,
                    bottom=y + h,
                    left=x
                )
                self.tracks[track_id].frames_since_update = 0
            else:
                # Tracking failed
                self.tracks[track_id].frames_since_update += 1
                if self.tracks[track_id].frames_since_update > self.max_disappeared:
                    tracks_to_remove.append(track_id)
        
        # Remove failed tracks
        for track_id in tracks_to_remove:
            if track_id in self.tracks:
                del self.tracks[track_id]
            if track_id in self.cv_trackers:
                del self.cv_trackers[track_id]
        
        return list(self.tracks.values())
    
    def _init_cv_tracker(self, frame: np.ndarray, track_id: int, box: BoundingBox):
        """Initialize OpenCV tracker for a track."""
        # Use CSRT tracker (accurate but slower) or KCF (faster)
        tracker = cv2.TrackerKCF_create()
        
        # Convert bbox to (x, y, w, h)
        bbox_xywh = (
            box.left,
            box.top,
            box.right - box.left,
            box.bottom - box.top
        )
        
        tracker.init(frame, bbox_xywh)
        self.cv_trackers[track_id] = tracker
    
    def _compute_iou(self, box1: BoundingBox, box2: BoundingBox) -> float:
        """Compute Intersection over Union between two boxes."""
        # Compute intersection
        x_left = max(box1.left, box2.left)
        y_top = max(box1.top, box2.top)
        x_right = min(box1.right, box2.right)
        y_bottom = min(box1.bottom, box2.bottom)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        
        # Compute union
        area1 = (box1.right - box1.left) * (box1.bottom - box1.top)
        area2 = (box2.right - box2.left) * (box2.bottom - box2.top)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def reset(self):
        """Reset all tracks."""
        self.tracks.clear()
        self.cv_trackers.clear()
        self.next_track_id = 0
        self.frame_count = 0
