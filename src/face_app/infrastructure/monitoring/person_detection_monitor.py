"""Generic person detection monitor - Track detections and trigger alerts."""
from datetime import datetime, timedelta
from typing import List, Optional, Callable
from dataclasses import dataclass


@dataclass
class PersonDetection:
    """A single person detection event."""
    timestamp: datetime
    name: str


class PersonDetectionMonitor:
    """Monitor person detections and trigger callback when threshold exceeded."""
    
    def __init__(
        self,
        person_name: str,
        time_window_seconds: int = 60,
        threshold: int = 10,
        alert_callback: Optional[Callable[[str, int, datetime], None]] = None,
        alert_cooldown_seconds: int = 300
    ):
        """
        Initialize person detection monitor.
        
        Args:
            person_name: Name of person to track (e.g., "Linh", "Stranger")
            time_window_seconds: Time window to count detections (default 60s)
            threshold: Number of detections to trigger alert
            alert_callback: Function to call when threshold exceeded (name, count, timestamp)
            alert_cooldown_seconds: Minimum seconds between alerts
        """
        self.person_name = person_name
        self.time_window_seconds = time_window_seconds
        self.threshold = threshold
        self.alert_callback = alert_callback
        self.alert_cooldown_seconds = alert_cooldown_seconds
        
        self.detections: List[PersonDetection] = []
        self.last_alert_time: Optional[datetime] = None
    
    def record_detection(self, detected_name: str) -> bool:
        """
        Record a detection and check if alert should be triggered.
        
        Args:
            detected_name: Name of detected person
            
        Returns:
            True if alert was triggered, False otherwise
        """
        now = datetime.now()
        
        # Only track detections for this specific person
        if detected_name != self.person_name:
            return False
        
        # Add new detection
        self.detections.append(PersonDetection(timestamp=now, name=detected_name))
        
        # Clean up old detections outside time window
        self._cleanup_old_detections(now)
        
        # Check if threshold exceeded
        return self._try_trigger_alert(now)
    
    def _cleanup_old_detections(self, now: datetime) -> None:
        """Remove detections outside the time window."""
        cutoff_time = now - timedelta(seconds=self.time_window_seconds)
        self.detections = [d for d in self.detections if d.timestamp > cutoff_time]
    
    def _try_trigger_alert(self, now: datetime) -> bool:
        """
        Check if alert should be triggered.
        
        Returns:
            True if alert was triggered, False otherwise
        """
        count = len(self.detections)
        
        # Check if threshold exceeded
        if count < self.threshold:
            return False
        
        # Check cooldown
        if self.last_alert_time:
            time_since_last = now - self.last_alert_time
            if time_since_last.total_seconds() < self.alert_cooldown_seconds:
                return False
        
        # Trigger alert
        self.last_alert_time = now
        if self.alert_callback:
            self.alert_callback(self.person_name, count, now)
        
        # Reset detections after alert
        self.detections = []
        
        return True
    
    def reset(self) -> None:
        """Reset all detections."""
        self.detections = []
        self.last_alert_time = None
    
    def get_status(self) -> dict:
        """
        Get current monitor status.
        
        Returns:
            Dictionary with current count and threshold
        """
        return {
            "person": self.person_name,
            "count": len(self.detections),
            "threshold": self.threshold,
            "time_window": self.time_window_seconds
        }
