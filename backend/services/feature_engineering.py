"""
Feature Engineering Service
Extract features từ motion events để feed vào AI model
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict
from backend.core.models import MotionEvent
import yaml
from pathlib import Path


class FeatureEngineer:
    """
    Extract và transform features từ motion events
    """
    
    @staticmethod
    def load_time_config():
        """Load time configuration from YAML file"""
        config_path = Path("config/time_config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config['features']['is_suspicious_definition']
        else:
            # Default fallback
            return {'suspicious_start': 15, 'suspicious_end': 18}
    
    @staticmethod
    def extract_time_features(timestamp: datetime) -> Dict:
        """
        Extract time-based features
        
        Args:
            timestamp: DateTime object
            
        Returns:
            Dictionary với time features
        """
        # Load time config
        time_config = FeatureEngineer.load_time_config()
        suspicious_start = time_config['suspicious_start']
        suspicious_end = time_config['suspicious_end']
        
        return {
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0,
            'is_night': 1 if (suspicious_start <= timestamp.hour < suspicious_end) else 0,
            'is_morning': 1 if 6 <= timestamp.hour <= 9 else 0,
            'is_evening': 1 if 18 <= timestamp.hour <= 23 else 0,
            'is_work_hours': 1 if (timestamp.weekday() < 5 and 9 <= timestamp.hour <= 17) else 0
        }
    
    @staticmethod
    def extract_motion_features(events: List[MotionEvent]) -> Dict:
        """
        Extract motion patterns từ event history
        
        Args:
            events: List of recent MotionEvents
            
        Returns:
            Dictionary với motion features
        """
        if not events:
            return {
                'frequency_5min': 0,
                'frequency_10min': 0,
                'frequency_30min': 0,
                'duration': 0,
                'avg_interval': 0
            }
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': pd.to_datetime(e.timestamp.replace('Z', '+00:00')),
            'motion': e.motion.value if hasattr(e.motion, 'value') else e.motion
        } for e in events])
        
        df = df.sort_values('timestamp')
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Calculate frequency (số lần phát hiện motion trong time windows)
        now = pd.Timestamp.now(tz='UTC')
        
        def count_in_window(minutes):
            cutoff = now - pd.Timedelta(minutes=minutes)
            return ((df['timestamp'] >= cutoff) & (df['motion'] == 1)).sum()
        
        frequency_5min = count_in_window(5)
        frequency_10min = count_in_window(10)
        frequency_30min = count_in_window(30)
        
        # Calculate duration (thời gian chuyển động liên tục)
        motion_events = df[df['motion'] == 1]
        if len(motion_events) > 0:
            latest_motion = motion_events.iloc[-1]['timestamp']
            duration = (now - latest_motion).total_seconds()
        else:
            duration = 0
        
        # Calculate average interval giữa các motion events
        if len(motion_events) > 1:
            intervals = motion_events['timestamp'].diff().dropna()
            avg_interval = intervals.mean().total_seconds() if len(intervals) > 0 else 0
        else:
            avg_interval = 0
        
        return {
            'frequency_5min': int(frequency_5min),
            'frequency_10min': int(frequency_10min),
            'frequency_30min': int(frequency_30min),
            'duration': float(duration),
            'avg_interval': float(avg_interval)
        }
    
    @staticmethod
    def extract_all_features(event: MotionEvent, history: List[MotionEvent] = None) -> Dict:
        """
        Extract tất cả features cho một event
        
        Args:
            event: Current MotionEvent
            history: List of recent events (for context)
            
        Returns:
            Dictionary với all features
        """
        if history is None:
            history = []
        
        # Parse timestamp
        timestamp = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
        
        # Time features
        time_features = FeatureEngineer.extract_time_features(timestamp)
        
        # Motion features
        motion_features = FeatureEngineer.extract_motion_features(history + [event])
        
        # Combine
        features = {
            **time_features,
            **motion_features,
            'motion': event.motion.value if hasattr(event.motion, 'value') else event.motion
        }
        
        return features
    
    @staticmethod
    def features_to_dataframe(features: Dict) -> pd.DataFrame:
        """Convert features dict to DataFrame for model input"""
        return pd.DataFrame([features])


def test_feature_engineering():
    """Test feature extraction"""
    print("=" * 60)
    print("TESTING FEATURE ENGINEERING")
    print("=" * 60)
    
    from backend.core.models import MotionEvent
    from backend.core.enums import MotionStatus
    
    # Create test events
    events = [
        MotionEvent(
            timestamp="2026-01-06T20:30:00Z",
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST",
            location="living_room"
        ),
        MotionEvent(
            timestamp="2026-01-06T20:32:00Z",
            motion=MotionStatus.NO_MOTION,
            sensor_id="TEST",
            location="living_room"
        ),
        MotionEvent(
            timestamp="2026-01-06T20:35:00Z",
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST",
            location="living_room"
        )
    ]
    
    # Extract features
    print("\n[Test 1] Time features:")
    time_features = FeatureEngineer.extract_time_features(datetime.now())
    for key, value in time_features.items():
        print(f"  {key}: {value}")
    
    print("\n[Test 2] Motion features:")
    motion_features = FeatureEngineer.extract_motion_features(events)
    for key, value in motion_features.items():
        print(f"  {key}: {value}")
    
    print("\n[Test 3] All features:")
    all_features = FeatureEngineer.extract_all_features(events[-1], events[:-1])
    for key, value in all_features.items():
        print(f"  {key}: {value}")
    
    print("\n[Test 4] DataFrame conversion:")
    df = FeatureEngineer.features_to_dataframe(all_features)
    print(df)
    
    print("\n" + "=" * 60)
    print("✅ Feature engineering tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_feature_engineering()
