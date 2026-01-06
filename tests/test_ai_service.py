"""
Unit Tests for AI Service
Tests AI prediction and feature engineering
"""

import pytest
import numpy as np
from datetime import datetime
from pathlib import Path
from backend.services.ai_service import AIService
from backend.core.models import MotionEvent, MotionStatus, PredictionLabel, AlertLevel


class TestAIService:
    """Test suite for AIService"""
    
    def test_ai_service_initialization(self, mock_model_path):
        """Test AI service initialization with model"""
        ai_service = AIService(model_path=mock_model_path)
        assert ai_service.model is not None
    
    def test_predict_daytime_motion(self, mock_model_path):
        """Test prediction for daytime motion (should be NORMAL)"""
        ai_service = AIService(model_path=mock_model_path)
        
        # Daytime motion event
        event = MotionEvent(
            timestamp=datetime(2026, 1, 6, 14, 0, 0),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        prediction = ai_service.predict(event, history=[])
        
        assert prediction is not None
        assert prediction.prediction_label in [PredictionLabel.NORMAL, PredictionLabel.SUSPICIOUS]
        assert 0 <= prediction.confidence <= 1
        assert prediction.alert_level in [AlertLevel.SAFE, AlertLevel.WARNING, AlertLevel.CRITICAL]
    
    def test_predict_nighttime_motion(self, mock_model_path):
        """Test prediction for nighttime motion (more likely SUSPICIOUS)"""
        ai_service = AIService(model_path=mock_model_path)
        
        # Nighttime motion event
        event = MotionEvent(
            timestamp=datetime(2026, 1, 6, 2, 0, 0),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        prediction = ai_service.predict(event, history=[])
        
        assert prediction is not None
        assert prediction.features['is_night'] == 1
        assert prediction.features['hour'] == 2
    
    def test_predict_with_history(self, mock_model_path):
        """Test prediction with event history"""
        ai_service = AIService(model_path=mock_model_path)
        
        # Create history
        history = [
            MotionEvent(
                timestamp=datetime(2026, 1, 6, 13, i, 0),
                motion=MotionStatus.MOTION_DETECTED,
                sensor_id="TEST_001",
                location="test"
            )
            for i in range(5)
        ]
        
        event = MotionEvent(
            timestamp=datetime(2026, 1, 6, 14, 0, 0),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        prediction = ai_service.predict(event, history=history)
        
        assert prediction is not None
        assert prediction.features['frequency_5min'] > 0
    
    def test_alert_level_critical(self, mock_model_path):
        """Test CRITICAL alert level for high confidence suspicious"""
        ai_service = AIService(model_path=mock_model_path)
        
        # Force suspicious prediction by nighttime
        event = MotionEvent(
            timestamp=datetime(2026, 1, 6, 3, 0, 0),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        prediction = ai_service.predict(event, history=[])
        
        # Alert level should be based on confidence
        if prediction.prediction_label == PredictionLabel.SUSPICIOUS and prediction.confidence > 0.8:
            assert prediction.alert_level == AlertLevel.CRITICAL
    
    def test_features_extraction(self, mock_model_path):
        """Test feature extraction from event"""
        ai_service = AIService(model_path=mock_model_path)
        
        event = MotionEvent(
            timestamp=datetime(2026, 1, 7, 15, 30, 0),  # Saturday afternoon
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        prediction = ai_service.predict(event, history=[])
        
        features = prediction.features
        assert 'hour' in features
        assert features['hour'] == 15
        assert 'day_of_week' in features
        assert 'is_night' in features
        assert features['is_night'] == 0  # Daytime
        assert 'frequency_5min' in features
        assert 'duration' in features


class TestFeatureEngineering:
    """Test suite for feature engineering"""
    
    def test_time_features(self):
        """Test time-based feature extraction"""
        from backend.services.feature_engineering import extract_time_features
        
        event = MotionEvent(
            timestamp=datetime(2026, 1, 6, 14, 30, 0),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        features = extract_time_features(event)
        
        assert features['hour'] == 14
        assert features['day_of_week'] == 1  # Tuesday
        assert features['is_night'] == 0
        assert features['is_weekend'] == 0
    
    def test_nighttime_detection(self):
        """Test nighttime detection"""
        from backend.services.feature_engineering import extract_time_features
        
        # Night event (2 AM)
        event = MotionEvent(
            timestamp=datetime(2026, 1, 6, 2, 0, 0),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        features = extract_time_features(event)
        assert features['is_night'] == 1
    
    def test_weekend_detection(self):
        """Test weekend detection"""
        from backend.services.feature_engineering import extract_time_features
        
        # Saturday
        event = MotionEvent(
            timestamp=datetime(2026, 1, 10, 14, 0, 0),  # Saturday
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        features = extract_time_features(event)
        assert features['is_weekend'] == 1
