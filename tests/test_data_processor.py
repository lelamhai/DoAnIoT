"""
Unit Tests for Data Processor Service
Tests validation and transformation logic
"""

import pytest
from datetime import datetime
from backend.services.data_processor import DataProcessor
from backend.core.models import MotionStatus


class TestDataProcessor:
    """Test suite for DataProcessor"""
    
    def test_validate_payload_valid(self, mqtt_payload_valid):
        """Test validation with valid payload"""
        result = DataProcessor.validate_payload(mqtt_payload_valid)
        assert result is True
    
    def test_validate_payload_invalid(self, mqtt_payload_invalid):
        """Test validation with invalid payload (missing fields)"""
        result = DataProcessor.validate_payload(mqtt_payload_invalid)
        assert result is False
    
    def test_validate_payload_missing_timestamp(self):
        """Test validation with missing timestamp"""
        payload = {"motion": 1}
        result = DataProcessor.validate_payload(payload)
        assert result is False
    
    def test_validate_payload_missing_motion(self):
        """Test validation with missing motion"""
        payload = {"timestamp": "2026-01-06T14:30:00"}
        result = DataProcessor.validate_payload(payload)
        assert result is False
    
    def test_transform_to_event_success(self, mqtt_payload_valid):
        """Test successful transformation to MotionEvent"""
        event = DataProcessor.transform_to_event(mqtt_payload_valid)
        
        assert event is not None
        assert event.motion == MotionStatus.MOTION_DETECTED
        assert event.sensor_id == "TEST_SENSOR_001"
        assert event.location == "test_room"
        assert isinstance(event.timestamp, datetime)
    
    def test_transform_to_event_no_motion(self):
        """Test transformation with motion=0"""
        payload = {
            "timestamp": "2026-01-06T14:30:00",
            "motion": 0,
            "sensor_id": "TEST_002"
        }
        event = DataProcessor.transform_to_event(payload)
        
        assert event is not None
        assert event.motion == MotionStatus.NO_MOTION
    
    def test_transform_to_event_defaults(self):
        """Test transformation with default values"""
        payload = {
            "timestamp": "2026-01-06T14:30:00",
            "motion": 1
        }
        event = DataProcessor.transform_to_event(payload)
        
        assert event is not None
        assert event.sensor_id == "PIR_001"  # Default
        assert event.location == "living_room"  # Default
    
    def test_transform_to_event_invalid_payload(self, mqtt_payload_invalid):
        """Test transformation with invalid payload"""
        event = DataProcessor.transform_to_event(mqtt_payload_invalid)
        assert event is None
    
    def test_transform_to_event_invalid_timestamp(self):
        """Test transformation with invalid timestamp format"""
        payload = {
            "timestamp": "invalid-timestamp",
            "motion": 1
        }
        event = DataProcessor.transform_to_event(payload)
        assert event is None
    
    def test_transform_to_event_invalid_motion_value(self):
        """Test transformation with invalid motion value"""
        payload = {
            "timestamp": "2026-01-06T14:30:00",
            "motion": 5  # Invalid: should be 0 or 1
        }
        event = DataProcessor.transform_to_event(payload)
        assert event is None
