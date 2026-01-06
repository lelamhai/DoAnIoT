"""
Domain Layer - Data Models
Định nghĩa các data models cốt lõi của hệ thống
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from backend.core.enums import MotionStatus, AlertLevel, PredictionLabel


@dataclass
class MotionEvent:
    """
    Model đại diện cho một sự kiện phát hiện chuyển động từ PIR sensor
    """
    timestamp: datetime
    motion: MotionStatus
    sensor_id: str = "PIR_001"
    location: str = "living_room"
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi sang dictionary để serialize"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "motion": self.motion.value,
            "sensor_id": self.sensor_id,
            "location": self.location
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MotionEvent':
        """Tạo MotionEvent từ dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            motion=MotionStatus(data["motion"]),
            sensor_id=data.get("sensor_id", "PIR_001"),
            location=data.get("location", "living_room")
        )


@dataclass
class Features:
    """
    Features được trích xuất từ MotionEvent để feed vào AI model
    """
    hour: int  # Giờ trong ngày (0-23)
    day_of_week: int  # Thứ trong tuần (0-6)
    is_night: int  # Có phải đêm khuya không (0/1)
    is_weekend: int  # Có phải cuối tuần không (0/1)
    motion_freq_10min: float  # Tần suất chuyển động trong 10 phút
    motion_freq_30min: float  # Tần suất chuyển động trong 30 phút
    motion_duration: int  # Thời gian liên tục có chuyển động
    
    def to_array(self) -> list:
        """Chuyển sang array để feed vào model"""
        return [
            self.hour,
            self.is_night,
            self.motion_freq_10min,
            self.motion_duration
        ]


@dataclass
class PredictionResult:
    """
    Kết quả dự đoán từ AI model
    """
    timestamp: datetime
    motion_event: MotionEvent
    is_abnormal: bool
    prediction_label: PredictionLabel
    confidence: float  # Độ tin cậy (0.0 - 1.0)
    alert_level: AlertLevel
    features: Optional[Features] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi sang dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "is_abnormal": self.is_abnormal,
            "prediction_label": self.prediction_label.value,
            "confidence": self.confidence,
            "alert_level": self.alert_level.value,
            "motion": self.motion_event.motion.value
        }


@dataclass
class SecurityEvent:
    """
    Model lưu trữ sự kiện an ninh trong database
    """
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    motion: int = 0
    sensor_id: str = "PIR_001"
    location: str = "living_room"
    prediction: Optional[str] = None  # "normal" hoặc "suspicious"
    alert_level: Optional[str] = None  # "safe", "warning", "critical"
    confidence: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
