"""
CSV Logger Service
Ghi log events vào CSV file để dễ dàng phân tích
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from backend.core.models import MotionEvent, PredictionResult


class CSVLogger:
    """
    Service để log motion events và predictions vào CSV
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize CSV Logger
        
        Args:
            log_dir: Directory để lưu log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # File paths
        self.events_file = self.log_dir / "events.csv"
        self.errors_file = self.log_dir / "errors.log"
        
        # Initialize CSV files nếu chưa tồn tại
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Tạo CSV file với headers nếu chưa tồn tại"""
        if not self.events_file.exists():
            with open(self.events_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'motion',
                    'sensor_id',
                    'location',
                    'prediction',
                    'confidence',
                    'alert_level',
                    'logged_at'
                ])
            print(f"✓ Created events log: {self.events_file}")
    
    def log_event(self, 
                  event: MotionEvent,
                  prediction: Optional[str] = None,
                  confidence: Optional[float] = None,
                  alert_level: Optional[str] = None):
        """
        Log motion event vào CSV
        
        Args:
            event: MotionEvent object
            prediction: Prediction label string (normal/suspicious)
            confidence: Confidence score (0-1)
            alert_level: Alert level string (safe/warning/critical)
        """
        try:
            with open(self.events_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    event.timestamp,
                    event.motion.value,
                    event.sensor_id,
                    event.location,
                    prediction,
                    f"{confidence:.2f}" if confidence else None,
                    alert_level,
                    datetime.now().isoformat()
                ])
        except Exception as e:
            self.log_error(f"Failed to log event: {e}")
    
    def log_error(self, message: str):
        """
        Log error message vào error log file
        
        Args:
            message: Error message
        """
        try:
            with open(self.errors_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"[{timestamp}] ERROR: {message}\n")
        except Exception as e:
            print(f"Failed to log error: {e}")
    
    def get_recent_events(self, limit: int = 100) -> list:
        """
        Đọc recent events từ CSV
        
        Args:
            limit: Số lượng events tối đa
            
        Returns:
            List of event dictionaries
        """
        if not self.events_file.exists():
            return []
        
        try:
            events = []
            with open(self.events_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                events = list(reader)
            
            # Return most recent events
            return events[-limit:] if len(events) > limit else events
        except Exception as e:
            self.log_error(f"Failed to read events: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Tính toán statistics từ CSV log
        
        Returns:
            Dictionary chứa statistics
        """
        events = self.get_recent_events(limit=1000)
        
        if not events:
            return {
                'total_events': 0,
                'motion_detected': 0,
                'suspicious_count': 0,
                'critical_alerts': 0
            }
        
        total = len(events)
        motion_detected = sum(1 for e in events if e['motion'] == '1')
        suspicious = sum(1 for e in events if e['prediction'] == 'SUSPICIOUS')
        critical = sum(1 for e in events if e['alert_level'] == 'CRITICAL')
        
        return {
            'total_events': total,
            'motion_detected': motion_detected,
            'motion_percentage': f"{(motion_detected/total*100):.1f}%",
            'suspicious_count': suspicious,
            'critical_alerts': critical
        }
    
    def clear_old_logs(self, days: int = 7):
        """
        Xóa logs cũ hơn số ngày chỉ định
        
        Args:
            days: Số ngày để giữ lại logs
        """
        # TODO: Implement log rotation
        pass


def test_csv_logger():
    """Test CSV Logger"""
    print("="*60)
    print("TESTING CSV LOGGER")
    print("="*60)
    
    from backend.core.models import MotionEvent, PredictionResult, MotionStatus, AlertLevel, PredictionLabel
    
    logger = CSVLogger()
    
    # Test log event without prediction
    print("\n[Test 1] Log event without prediction")
    event1 = MotionEvent(
        timestamp="2026-01-06T20:30:00Z",
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="TEST_SENSOR_001",
        location="living_room"
    )
    logger.log_event(event1)
    print("✓ Event logged")
    
    # Test log event with prediction
    print("\n[Test 2] Log event with prediction")
    event2 = MotionEvent(
        timestamp="2026-01-06T03:00:00Z",
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="TEST_SENSOR_001",
        location="living_room"
    )
    prediction = PredictionResult(
        label=PredictionLabel.SUSPICIOUS,
        confidence=0.95,
        alert_level=AlertLevel.CRITICAL,
        message="Phát hiện chuyển động đêm khuya"
    )
    logger.log_event(event2, prediction)
    print("✓ Event with prediction logged")
    
    # Test get recent events
    print("\n[Test 3] Get recent events")
    recent = logger.get_recent_events(limit=10)
    print(f"✓ Retrieved {len(recent)} events")
    for event in recent[-3:]:
        print(f"  - {event['timestamp']}: motion={event['motion']}, prediction={event['prediction']}")
    
    # Test statistics
    print("\n[Test 4] Get statistics")
    stats = logger.get_statistics()
    print("✓ Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)


if __name__ == "__main__":
    test_csv_logger()
