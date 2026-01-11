"""Monitoring infrastructure - Stranger detection."""
from face_app.infrastructure.monitoring.stranger_monitor import StrangerMonitor
from face_app.infrastructure.monitoring.person_detection_monitor import PersonDetectionMonitor

__all__ = ["StrangerMonitor", "PersonDetectionMonitor"]
