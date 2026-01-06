"""
Application Layer - Data Processor
Xử lý validation và transformation của dữ liệu từ MQTT
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
from backend.core.models import MotionEvent
from backend.core.enums import MotionStatus


class DataProcessor:
    """
    Data Processor để validate và transform MQTT payloads
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def validate_payload(payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate MQTT payload
        
        Args:
            payload: Dictionary data từ MQTT message
            
        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        required_fields = ["timestamp", "motion"]
        
        for field in required_fields:
            if field not in payload:
                return False, f"Missing required field: {field}"
        
        # Validate motion value
        motion = payload.get("motion")
        if motion not in [0, 1]:
            return False, f"Invalid motion value: {motion}. Must be 0 or 1"
        
        # Validate timestamp format
        try:
            datetime.fromisoformat(payload["timestamp"])
        except (ValueError, TypeError) as e:
            return False, f"Invalid timestamp format: {e}"
        
        return True, None
    
    def transform_to_event(self, payload: Dict[str, Any]) -> Optional[MotionEvent]:
        """
        Transform MQTT payload thành MotionEvent object
        
        Args:
            payload: Dictionary data từ MQTT
            
        Returns:
            MotionEvent object hoặc None nếu validation fail
        """
        # Validate trước
        is_valid, error = self.validate_payload(payload)
        if not is_valid:
            self.logger.error(f"Payload validation failed: {error}")
            return None
        
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(payload["timestamp"])
            
            # Parse motion status
            motion_value = int(payload["motion"])
            motion = MotionStatus.MOTION_DETECTED if motion_value == 1 else MotionStatus.NO_MOTION
            
            # Optional fields
            sensor_id = payload.get("sensor_id", "PIR_001")
            location = payload.get("location", "living_room")
            
            # Create MotionEvent
            event = MotionEvent(
                timestamp=timestamp,
                motion=motion,
                sensor_id=sensor_id,
                location=location
            )
            
            self.logger.debug(f"Transformed payload to MotionEvent: {event}")
            return event
            
        except Exception as e:
            self.logger.error(f"Error transforming payload: {e}")
            return None
    
    def sanitize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Làm sạch và chuẩn hóa payload
        
        Args:
            payload: Raw payload
            
        Returns:
            Cleaned payload
        """
        cleaned = {}
        
        # Copy timestamp
        if "timestamp" in payload:
            cleaned["timestamp"] = str(payload["timestamp"])
        else:
            cleaned["timestamp"] = datetime.now().isoformat()
        
        # Ensure motion is int 0 or 1
        if "motion" in payload:
            try:
                motion = int(payload["motion"])
                cleaned["motion"] = 1 if motion > 0 else 0
            except (ValueError, TypeError):
                cleaned["motion"] = 0
        
        # Copy optional fields
        if "sensor_id" in payload:
            cleaned["sensor_id"] = str(payload["sensor_id"])
        
        if "location" in payload:
            cleaned["location"] = str(payload["location"])
        
        return cleaned
    
    def process_message(self, payload: Dict[str, Any]) -> Optional[MotionEvent]:
        """
        Process complete: sanitize → validate → transform
        
        Args:
            payload: Raw MQTT payload
            
        Returns:
            MotionEvent object hoặc None nếu processing fail
        """
        # Step 1: Sanitize
        cleaned_payload = self.sanitize_payload(payload)
        self.logger.debug(f"Sanitized payload: {cleaned_payload}")
        
        # Step 2: Validate & Transform
        event = self.transform_to_event(cleaned_payload)
        
        return event


class DataValidator:
    """
    Helper class cho validation rules
    """
    
    @staticmethod
    def is_valid_motion(value: Any) -> bool:
        """Check if motion value is valid (0 or 1)"""
        try:
            return int(value) in [0, 1]
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_timestamp(value: Any) -> bool:
        """Check if timestamp is valid ISO format"""
        try:
            datetime.fromisoformat(str(value))
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_sensor_id(value: Any) -> bool:
        """Check if sensor_id is valid string"""
        return isinstance(value, str) and len(value) > 0


if __name__ == "__main__":
    # Test DataProcessor
    logging.basicConfig(level=logging.DEBUG)
    
    processor = DataProcessor()
    
    # Test valid payload
    print("=== Test Valid Payload ===")
    valid_payload = {
        "timestamp": "2026-01-06T10:00:00",
        "motion": 1,
        "sensor_id": "PIR_001",
        "location": "living_room"
    }
    
    event = processor.process_message(valid_payload)
    if event:
        print(f"✅ Success: {event}")
        print(f"   Event dict: {event.to_dict()}")
    else:
        print("❌ Failed to process")
    
    # Test invalid payload
    print("\n=== Test Invalid Payload ===")
    invalid_payload = {
        "timestamp": "invalid-timestamp",
        "motion": 2  # Invalid value
    }
    
    event = processor.process_message(invalid_payload)
    if event:
        print(f"Event: {event}")
    else:
        print("❌ Correctly rejected invalid payload")
    
    # Test missing fields
    print("\n=== Test Missing Fields ===")
    incomplete_payload = {
        "motion": 1
        # Missing timestamp
    }
    
    event = processor.process_message(incomplete_payload)
    if event:
        print(f"✅ Auto-filled timestamp: {event.timestamp}")
    else:
        print("❌ Failed")
