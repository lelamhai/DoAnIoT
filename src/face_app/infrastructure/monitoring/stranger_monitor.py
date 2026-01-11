"""Stranger detection monitor - Track and alert on suspicious activity."""
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass


@dataclass
class StrangerDetection:
    """A single stranger detection event."""
    timestamp: datetime
    name: str = "Stranger"


class StrangerMonitor:
    """Monitor stranger detections and trigger alerts."""
    
    def __init__(
        self,
        time_window_seconds: int = 60,  # 1 minute
        threshold: int = 10,  # 10 detections
        alert_callback=None,
        alert_cooldown_seconds: int = 300  # 5 minutes between alerts
    ):
        """
        Initialize stranger monitor.
        
        Args:
            time_window_seconds: Time window to count detections (default 60s = 1 minute)
            threshold: Number of stranger detections to trigger alert
            alert_callback: Function to call when threshold exceeded
            alert_cooldown_seconds: Minimum seconds between alerts (default 300s = 5 minutes)
        """
        self.time_window_seconds = time_window_seconds
        self.threshold = threshold
        self.alert_callback = alert_callback
        self.alert_cooldown_seconds = alert_cooldown_seconds
        
        self.detections: List[StrangerDetection] = []
        self.last_alert_time = None
    
    def record_detection(self, is_stranger: bool, name: str = "Stranger") -> bool:
        """
        Record a detection and check if alert should be triggered.
        
        Args:
            is_stranger: True if stranger detected
            name: Name of detected person
            
        Returns:
            True if alert was triggered
        """
        if not is_stranger:
            return False
        
        now = datetime.now()
        
        # Add detection
        self.detections.append(StrangerDetection(timestamp=now, name=name))
        
        # Clean up old detections (outside time window)
        self._cleanup_old_detections(now)
        
        # Check if we should trigger alert
        count = len(self.detections)
        
        if count >= self.threshold:
            return self._try_trigger_alert(count, now)
        
        return False
    
    def _cleanup_old_detections(self, current_time: datetime):
        """Remove detections older than time window."""
        cutoff_time = current_time - timedelta(seconds=self.time_window_seconds)
        self.detections = [
            d for d in self.detections 
            if d.timestamp >= cutoff_time
        ]
    
    def _try_trigger_alert(self, count: int, current_time: datetime) -> bool:
        """
        Try to trigger alert if threshold exceeded and not in cooldown.
        
        Args:
            count: Current stranger count
            current_time: Current timestamp
            
        Returns:
            True if alert was triggered
        """
        # Check cooldown
        if self.last_alert_time:
            time_since_last = (current_time - self.last_alert_time).total_seconds()
            if time_since_last < self.alert_cooldown_seconds:
                # Still in cooldown
                return False
        
        # Trigger alert
        print(f"\n🚨 CẢNH BÁO: Phát hiện {count} người lạ trong {self.time_window_seconds}s!")
        
        if self.alert_callback:
            try:
                self.alert_callback(count, current_time)
            except Exception as e:
                print(f"❌ Error sending alert: {e}")
        
        self.last_alert_time = current_time
        
        # Reset counter after alert
        self.reset()
        
        return True
    
    def reset(self):
        """Reset detection counter."""
        self.detections.clear()
        print(f"♻️  Đã reset bộ đếm người lạ")
    
    def get_current_count(self) -> int:
        """Get current stranger count in window."""
        self._cleanup_old_detections(datetime.now())
        return len(self.detections)
    
    def get_status(self) -> dict:
        """Get current monitor status."""
        count = self.get_current_count()
        return {
            'current_count': count,
            'threshold': self.threshold,
            'time_window_seconds': self.time_window_seconds,
            'percentage': (count / self.threshold) * 100 if self.threshold > 0 else 0,
            'alert_ready': count >= self.threshold
        }
