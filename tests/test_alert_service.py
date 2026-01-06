"""
Unit Tests for Alert Service
Tests multi-channel alert functionality
"""

import pytest
from datetime import datetime
from backend.services.alert_service import AlertService
from backend.core.models import MotionEvent, MotionStatus, PredictionResult, PredictionLabel, AlertLevel
from backend.infrastructure.config import AlertConfig


class TestAlertService:
    """Test suite for AlertService"""
    
    def test_alert_service_initialization(self):
        """Test alert service initialization"""
        config = AlertConfig()
        alert_service = AlertService(config)
        
        assert alert_service is not None
        assert 'console' in alert_service.enabled_channels
    
    def test_should_alert_critical(self):
        """Test alert triggering for CRITICAL level"""
        alert_service = AlertService()
        
        event = MotionEvent(
            timestamp=datetime.now(),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        prediction = PredictionResult(
            timestamp=datetime.now(),
            motion_event=event,
            prediction_label=PredictionLabel.SUSPICIOUS,
            confidence=0.95,
            alert_level=AlertLevel.CRITICAL,
            features={'hour': 2, 'is_night': 1}
        )
        
        # Critical should always trigger alert
        should_alert = alert_service._should_alert(prediction)
        assert should_alert is True
    
    def test_should_alert_safe(self):
        """Test no alert for SAFE level"""
        alert_service = AlertService()
        
        event = MotionEvent(
            timestamp=datetime.now(),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        prediction = PredictionResult(
            timestamp=datetime.now(),
            motion_event=event,
            prediction_label=PredictionLabel.NORMAL,
            confidence=0.90,
            alert_level=AlertLevel.SAFE,
            features={'hour': 14, 'is_night': 0}
        )
        
        should_alert = alert_service._should_alert(prediction)
        assert should_alert is False
    
    def test_format_alert_message(self):
        """Test alert message formatting"""
        alert_service = AlertService()
        
        event = MotionEvent(
            timestamp=datetime(2026, 1, 6, 2, 30, 0),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_SENSOR_001",
            location="Living Room"
        )
        
        prediction = PredictionResult(
            timestamp=datetime(2026, 1, 6, 2, 30, 0),
            motion_event=event,
            prediction_label=PredictionLabel.SUSPICIOUS,
            confidence=0.95,
            alert_level=AlertLevel.CRITICAL,
            features={'hour': 2, 'is_night': 1, 'frequency_5min': 5}
        )
        
        message = alert_service._format_alert_message(event, prediction)
        
        assert "CRITICAL" in message
        assert "Living Room" in message
        assert "SUSPICIOUS" in message
        assert "95" in message  # Confidence percentage
    
    def test_format_alert_subject(self):
        """Test alert subject formatting"""
        alert_service = AlertService()
        
        event = MotionEvent(
            timestamp=datetime.now(),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="TEST_001",
            location="test"
        )
        
        prediction_critical = PredictionResult(
            timestamp=datetime.now(),
            motion_event=event,
            prediction_label=PredictionLabel.SUSPICIOUS,
            confidence=0.95,
            alert_level=AlertLevel.CRITICAL,
            features={}
        )
        
        subject = alert_service._format_alert_subject(prediction_critical)
        
        assert "CRITICAL" in subject
        assert "Alert" in subject or "alert" in subject
    
    def test_console_alert(self, capsys):
        """Test console alert output"""
        alert_service = AlertService()
        
        subject = "TEST ALERT"
        message = "This is a test alert message"
        
        alert_service._send_console_alert(subject, message)
        
        captured = capsys.readouterr()
        assert "TEST ALERT" in captured.out
        assert "test alert message" in captured.out
    
    def test_test_connection_console(self):
        """Test connection testing for console (always works)"""
        alert_service = AlertService()
        
        results = alert_service.test_connection()
        
        assert 'console' in results
        assert results['console'] is True
    
    def test_email_config_disabled(self):
        """Test email alerts when disabled"""
        config = AlertConfig(email_enabled=False)
        alert_service = AlertService(config)
        
        assert 'email' not in alert_service.enabled_channels
    
    def test_telegram_config_disabled(self):
        """Test Telegram alerts when disabled"""
        config = AlertConfig(telegram_enabled=False)
        alert_service = AlertService(config)
        
        assert 'telegram' not in alert_service.enabled_channels
    
    def test_send_alert_force(self):
        """Test forced alert sending (ignores thresholds)"""
        alert_service = AlertService()
        
        event = MotionEvent(
            timestamp=datetime.now(),
            motion=MotionStatus.NO_MOTION,
            sensor_id="TEST_001",
            location="test"
        )
        
        # SAFE prediction (normally wouldn't trigger alert)
        prediction = PredictionResult(
            timestamp=datetime.now(),
            motion_event=event,
            prediction_label=PredictionLabel.NORMAL,
            confidence=0.90,
            alert_level=AlertLevel.SAFE,
            features={}
        )
        
        # Force=True should send alert anyway
        result = alert_service.send_alert(event, prediction, force=True)
        
        # Should succeed (console always works)
        assert result is True
