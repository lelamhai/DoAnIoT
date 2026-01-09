"""Multi-threaded camera capture and recognition for better performance."""
import cv2
import numpy as np
from threading import Thread, Lock
from queue import Queue
from typing import Optional
from face_app.domain.ports import CameraPort


class ThreadedCamera(CameraPort):
    """Camera with threaded capture for better FPS."""
    
    def __init__(self, camera_index: int = 0, buffer_size: int = 2):
        """
        Initialize threaded camera.
        
        Args:
            camera_index: Camera device index
            buffer_size: Max frames in buffer (lower = less latency)
        """
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {camera_index}")
        
        # Thread-safe frame storage
        self.frame_queue = Queue(maxsize=buffer_size)
        self.stopped = False
        self.lock = Lock()
        
        # Start capture thread
        self.thread = Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        
        print(f"✅ Threaded camera initialized (index: {camera_index})")
    
    def _capture_loop(self):
        """Capture frames in background thread."""
        while not self.stopped:
            ret, frame = self.cap.read()
            
            if not ret:
                continue
            
            # Add to queue (drop old if full)
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except:
                    pass
            
            try:
                self.frame_queue.put(frame, block=False)
            except:
                pass
    
    def read(self) -> tuple:
        """
        Read latest frame from queue.
        
        Returns:
            (success, frame)
        """
        if self.frame_queue.empty():
            return False, None
        
        try:
            frame = self.frame_queue.get(timeout=1.0)
            return True, frame
        except:
            return False, None
    
    def release(self):
        """Stop capture thread and release camera."""
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
    
    def is_opened(self) -> bool:
        """Check if camera is opened."""
        return self.cap.isOpened() and not self.stopped
    
    def __del__(self):
        """Cleanup on deletion."""
        self.release()


class AsyncRecognitionPipeline:
    """Asynchronous recognition pipeline with separate threads for capture and processing."""
    
    def __init__(self, recognize_usecase, queue_size: int = 5):
        """
        Initialize async pipeline.
        
        Args:
            recognize_usecase: Recognition use case
            queue_size: Size of processing queue
        """
        self.recognize_usecase = recognize_usecase
        self.frame_queue = Queue(maxsize=queue_size)
        self.result_queue = Queue(maxsize=queue_size)
        
        self.processing = False
        self.lock = Lock()
        
        # Processing thread
        self.process_thread = None
    
    def start(self):
        """Start processing thread."""
        if not self.processing:
            self.processing = True
            self.process_thread = Thread(target=self._process_loop, daemon=True)
            self.process_thread.start()
            print("✅ Async recognition pipeline started")
    
    def stop(self):
        """Stop processing thread."""
        self.processing = False
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=2.0)
        print("👋 Async recognition pipeline stopped")
    
    def submit_frame(self, frame: np.ndarray) -> bool:
        """
        Submit frame for processing.
        
        Args:
            frame: BGR frame
            
        Returns:
            True if submitted successfully
        """
        if self.frame_queue.full():
            # Drop oldest frame
            try:
                self.frame_queue.get_nowait()
            except:
                pass
        
        try:
            self.frame_queue.put(frame, block=False)
            return True
        except:
            return False
    
    def get_result(self, timeout: float = 0.01):
        """
        Get latest recognition result.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Recognition result or None
        """
        try:
            return self.result_queue.get(timeout=timeout)
        except:
            return None
    
    def _process_loop(self):
        """Process frames in background thread."""
        while self.processing:
            try:
                frame = self.frame_queue.get(timeout=0.1)
            except:
                continue
            
            # Run recognition
            result = self.recognize_usecase.execute(frame)
            
            # Store result
            if self.result_queue.full():
                try:
                    self.result_queue.get_nowait()
                except:
                    pass
            
            try:
                self.result_queue.put(result, block=False)
            except:
                pass
