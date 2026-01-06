"""
AI Service
Prediction service sử dụng trained model để classify motion events
"""

import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from backend.core.models import MotionEvent, PredictionResult
from backend.core.enums import AlertLevel, PredictionLabel
from backend.services.feature_engineering import FeatureEngineer


class AIService:
    """
    AI prediction service
    Load trained model và perform real-time classification
    """
    
    def __init__(self, model_path: str = "ai_model/models/classifier.pkl"):
        """
        Initialize AI service với trained model
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = Path(model_path)
        self.model_data = None
        self.model = None
        self.feature_columns = None
        self.load_model()
    
    def load_model(self):
        """Load trained model from disk"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                f"Please train the model first: python ai_model/train.py"
            )
        
        self.model_data = joblib.load(self.model_path)
        self.model = self.model_data['model']
        self.feature_columns = self.model_data['feature_columns']
        
        print(f"  AI Model loaded: {self.model_data['model_type']}")
    
    def predict(self, event: MotionEvent, history: List[MotionEvent] = None) -> PredictionResult:
        """
        Predict Normal/Suspicious cho một motion event
        
        Args:
            event: Current MotionEvent
            history: List of recent events for context
            
        Returns:
            PredictionResult với prediction và confidence
        """
        if history is None:
            history = []
        
        # Extract features
        features = FeatureEngineer.extract_all_features(event, history)
        
        # Prepare DataFrame với đúng columns order
        X = pd.DataFrame([{col: features.get(col, 0) for col in self.feature_columns}])
        
        # Predict
        prediction = self.model.predict(X)[0]  # 0=Normal, 1=Suspicious
        probabilities = self.model.predict_proba(X)[0]
        
        # Determine alert level
        is_abnormal = (prediction == 1)
        confidence = probabilities[1] if is_abnormal else probabilities[0]
        
        if is_abnormal:
            prediction_label = PredictionLabel.SUSPICIOUS
            if confidence > 0.8:
                alert_level = AlertLevel.CRITICAL
            else:
                alert_level = AlertLevel.WARNING
        else:
            prediction_label = PredictionLabel.NORMAL
            alert_level = AlertLevel.SAFE
        
        # Parse timestamp from event
        event_timestamp = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
        
        return PredictionResult(
            timestamp=event_timestamp,
            motion_event=event,
            is_abnormal=is_abnormal,
            prediction_label=prediction_label,
            confidence=float(confidence),
            alert_level=alert_level,
            features=None  # Can add Features object here if needed
        )
    
    def batch_predict(self, events: List[MotionEvent]) -> List[PredictionResult]:
        """
        Predict cho nhiều events cùng lúc
        
        Args:
            events: List of MotionEvents
            
        Returns:
            List of PredictionResults
        """
        results = []
        for i, event in enumerate(events):
            history = events[:i]  # Use previous events as history
            result = self.predict(event, history)
            results.append(result)
        return results


def test_ai_service():
    """Test AI service"""
    print("=" * 60)
    print("TESTING AI SERVICE")
    print("=" * 60)
    
    from backend.core.models import MotionEvent
    from backend.core.enums import MotionStatus
    
    # Check if model exists
    model_path = Path("ai_model/models/classifier.pkl")
    if not model_path.exists():
        print("\n❌ Model not found. Train first:")
        print("   python ai_model/train.py")
        return
    
    # Initialize service
    print("\n[1] Initializing AI Service...")
    ai_service = AIService()
    
    # Test scenarios
    test_cases = [
        {
            'name': 'Sáng đi làm',
            'timestamp': '2026-01-06T07:30:00Z',
            'motion': MotionStatus.MOTION_DETECTED
        },
        {
            'name': 'Đêm khuya có chuyển động',
            'timestamp': '2026-01-06T02:30:00Z',
            'motion': MotionStatus.MOTION_DETECTED
        },
        {
            'name': 'Giờ làm việc có người',
            'timestamp': '2026-01-06T14:00:00Z',
            'motion': MotionStatus.MOTION_DETECTED
        }
    ]
    
    print("\n[2] Testing predictions:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {test_case['name']}")
        
        # Create event
        event = MotionEvent(
            timestamp=test_case['timestamp'],
            motion=test_case['motion'],
            sensor_id="TEST",
            location="living_room"
        )
        
        # Predict
        result = ai_service.predict(event)
        
        # Display
        status = "SUSPICIOUS" if result.is_abnormal else "NORMAL"
        symbol = "🔴" if result.is_abnormal else "🟢"
        print(f"    Prediction: {symbol} {status}")
        print(f"    Confidence: {result.confidence:.2%}")
        print(f"    Alert Level: {result.alert_level.value}")
        print(f"    Features: {result.features}")
    
    print("\n" + "=" * 60)
    print("✅ AI Service tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_ai_service()
