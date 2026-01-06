"""
AI Motion Classifier - Rule-Based
Phân loại chuyển động: NORMAL, SUSPICIOUS, NOISE
"""

import yaml
from datetime import datetime
from typing import Dict, Tuple
from pathlib import Path
from backend.core.enums import AlertLevel, PredictionLabel
from backend.core.models import MotionEvent, PredictionResult


class RuleBasedClassifier:
    """
    Rule-based classifier cho motion events
    Dùng config file để customize rules
    """
    
    def __init__(self, config_path: str = "config/ai_rules_config.yaml"):
        """Load AI rules từ config file"""
        self.config_path = Path(config_path)
        self.rules = self._load_rules()
        self.motion_history = []  # Track recent motions
        
    def _load_rules(self) -> Dict:
        """Load rules từ YAML config"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config.get('classification_rules', {})
    
    def reload_rules(self):
        """Reload rules từ config (để update trong demo)"""
        self.rules = self._load_rules()
        print("✓ Rules reloaded successfully")
    
    def classify(self, event: MotionEvent) -> PredictionResult:
        """
        Phân loại motion event theo rules
        
        Args:
            event: MotionEvent cần classify
            
        Returns:
            PredictionResult với label, confidence, alert_level
        """
        # Parse timestamp
        timestamp = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
        hour = timestamp.hour
        day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
        
        # Track motion history
        self._update_history(event)
        
        # Calculate features
        frequency = self._calculate_frequency()
        duration = self._calculate_duration()
        
        # Apply rules theo thứ tự ưu tiên
        
        # Rule 1: Đêm khuya (ưu tiên cao nhất)
        if self.rules.get('night_hours', {}).get('enabled', False):
            result = self._check_night_hours(hour)
            if result:
                return result
        
        # Rule 2: Giờ làm việc
        if self.rules.get('work_hours', {}).get('enabled', False):
            result = self._check_work_hours(hour, day_of_week)
            if result:
                return result
        
        # Rule 3: Rapid motion (nhiễu)
        if self.rules.get('rapid_motion', {}).get('enabled', False):
            result = self._check_rapid_motion(frequency, duration)
            if result:
                return result
        
        # Rule 4: Prolonged motion
        if self.rules.get('prolonged_motion', {}).get('enabled', False):
            result = self._check_prolonged_motion(duration)
            if result:
                return result
        
        # Default: NORMAL
        return PredictionResult(
            label=PredictionLabel.NORMAL,
            confidence=0.85,
            alert_level=AlertLevel.SAFE,
            message="Chuyển động bình thường trong khung giờ sinh hoạt"
        )
    
    def _check_night_hours(self, hour: int) -> PredictionResult:
        """Check rule: Đêm khuya"""
        rule = self.rules['night_hours']
        start = rule['start_hour']
        end = rule['end_hour']
        
        if start <= hour <= end:
            return PredictionResult(
                label=PredictionLabel.SUSPICIOUS,
                confidence=rule['confidence'],
                alert_level=AlertLevel[rule['alert_level']],
                message=rule['message']
            )
        return None
    
    def _check_work_hours(self, hour: int, day_of_week: int) -> PredictionResult:
        """Check rule: Giờ làm việc"""
        rule = self.rules['work_hours']
        start = rule['start_hour']
        end = rule['end_hour']
        weekdays_only = rule.get('weekdays_only', False)
        
        # Nếu là weekday (0-4 = Thứ 2-6) và trong giờ làm việc
        if weekdays_only and day_of_week > 4:
            return None  # Cuối tuần thì skip rule này
        
        if start <= hour <= end:
            return PredictionResult(
                label=PredictionLabel.SUSPICIOUS,
                confidence=rule['confidence'],
                alert_level=AlertLevel[rule['alert_level']],
                message=rule['message']
            )
        return None
    
    def _check_rapid_motion(self, frequency: int, duration: float) -> PredictionResult:
        """Check rule: Chuyển động quá nhanh (nhiễu)"""
        rule = self.rules['rapid_motion']
        freq_threshold = rule['frequency_threshold']
        duration_max = rule['duration_max']
        
        if frequency > freq_threshold and duration < duration_max:
            return PredictionResult(
                label=PredictionLabel.NORMAL,  # Nhiễu không phải suspicious
                confidence=rule['confidence'],
                alert_level=AlertLevel[rule['alert_level']],
                message=rule['message']
            )
        return None
    
    def _check_prolonged_motion(self, duration: float) -> PredictionResult:
        """Check rule: Chuyển động kéo dài"""
        rule = self.rules['prolonged_motion']
        duration_min = rule['duration_min']
        
        if duration > duration_min:
            return PredictionResult(
                label=PredictionLabel.SUSPICIOUS,
                confidence=rule['confidence'],
                alert_level=AlertLevel[rule['alert_level']],
                message=rule['message']
            )
        return None
    
    def _update_history(self, event: MotionEvent):
        """Update motion history (giữ 5 phút gần nhất)"""
        self.motion_history.append({
            'timestamp': datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')),
            'motion': event.motion
        })
        
        # Giữ tối đa 5 phút history
        now = datetime.now()
        self.motion_history = [
            m for m in self.motion_history
            if (now - m['timestamp']).total_seconds() <= 300
        ]
    
    def _calculate_frequency(self) -> int:
        """Tính tần suất phát hiện trong 1 phút gần nhất"""
        if not self.motion_history:
            return 0
        
        now = datetime.now()
        recent = [
            m for m in self.motion_history
            if (now - m['timestamp']).total_seconds() <= 60
            and m['motion'] == 1
        ]
        return len(recent)
    
    def _calculate_duration(self) -> float:
        """Tính thời gian chuyển động liên tục (giây)"""
        if not self.motion_history:
            return 0.0
        
        # Tính từ lần motion=1 gần nhất
        motion_events = [m for m in self.motion_history if m['motion'] == 1]
        if not motion_events:
            return 0.0
        
        latest = motion_events[-1]['timestamp']
        now = datetime.now()
        return (now - latest).total_seconds()


def test_classifier():
    """Test classifier với demo scenarios"""
    print("=" * 60)
    print("TESTING AI CLASSIFIER WITH DEMO SCENARIOS")
    print("=" * 60)
    
    classifier = RuleBasedClassifier()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Chuyển động bình thường tối",
            "timestamp": "2026-01-06T20:30:00Z",
            "expected": "NORMAL"
        },
        {
            "name": "Phát hiện trộm 3h sáng",
            "timestamp": "2026-01-06T03:00:00Z",
            "expected": "SUSPICIOUS"
        },
        {
            "name": "Có người khi đi làm (14h Thứ 3)",
            "timestamp": "2026-01-07T14:00:00Z",
            "expected": "SUSPICIOUS"
        },
        {
            "name": "Cuối tuần ban ngày",
            "timestamp": "2026-01-11T14:00:00Z",  # Saturday
            "expected": "NORMAL"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[Scenario {i}] {scenario['name']}")
        print(f"  Timestamp: {scenario['timestamp']}")
        
        event = MotionEvent(
            timestamp=scenario['timestamp'],
            motion=1,
            sensor_id="TEST_SENSOR",
            location="living_room"
        )
        
        result = classifier.classify(event)
        
        print(f"  Result: {result.label.value}")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Alert Level: {result.alert_level.value}")
        print(f"  Message: {result.message}")
        print(f"  Expected: {scenario['expected']}")
        
        match = "✓ PASS" if result.label.value.upper() == scenario['expected'] else "✗ FAIL"
        print(f"  {match}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_classifier()
