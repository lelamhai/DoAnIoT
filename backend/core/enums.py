"""
Domain Layer - Enums
Định nghĩa các enum cho business logic
"""

from enum import Enum


class MotionStatus(Enum):
    """Trạng thái phát hiện chuyển động từ PIR sensor"""
    NO_MOTION = 0
    MOTION_DETECTED = 1


class AlertLevel(Enum):
    """Mức độ cảnh báo của hệ thống"""
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"


class PredictionLabel(Enum):
    """Kết quả phân loại từ AI model"""
    NORMAL = 0  # Hành vi bình thường
    SUSPICIOUS = 1  # Hành vi đáng ngờ/xâm nhập
