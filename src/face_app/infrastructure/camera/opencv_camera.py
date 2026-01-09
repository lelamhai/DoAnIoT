"""OpenCV camera adapter."""
from typing import Tuple
import numpy as np
import cv2
from face_app.domain.ports import CameraPort
from face_app.config.settings import CAMERA_INDEX


class OpenCVCamera(CameraPort):
    """Adapter for OpenCV VideoCapture."""
    
    def __init__(self, camera_index: int = CAMERA_INDEX):
        """
        Initialize camera.
        
        Args:
            camera_index: Camera device index (0 = default)
        """
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {camera_index}")
    
    def read(self) -> Tuple[bool, np.ndarray]:
        """
        Read a frame from camera.
        
        Returns:
            (success, frame_bgr)
        """
        return self.cap.read()
    
    def release(self) -> None:
        """Release camera resources."""
        if self.cap:
            self.cap.release()
    
    def is_opened(self) -> bool:
        """Check if camera is opened."""
        return self.cap.isOpened()
    
    def __del__(self):
        """Ensure camera is released on deletion."""
        self.release()
