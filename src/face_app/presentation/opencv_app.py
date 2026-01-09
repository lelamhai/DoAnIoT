"""OpenCV presentation layer - UI for face recognition."""
import cv2
import numpy as np
from face_app.domain.ports import CameraPort
from face_app.application.usecases.recognize_frame import RecognizeFrameUseCase
from face_app.application.dto import RecognitionResult
from face_app.config.settings import (
    BBOX_THICKNESS, FONT, FONT_SCALE, FONT_THICKNESS,
    BBOX_COLOR_KNOWN, BBOX_COLOR_UNKNOWN
)


class OpenCVApp:
    """OpenCV-based UI for face recognition."""
    
    def __init__(
        self,
        camera: CameraPort,
        recognize_usecase: RecognizeFrameUseCase,
        window_name: str = "Face Recognition - Press 'q' to quit"
    ):
        """
        Initialize OpenCV app.
        
        Args:
            camera: Camera port
            recognize_usecase: Use case for recognizing frames
            window_name: Window title
        """
        self.camera = camera
        self.recognize_usecase = recognize_usecase
        self.window_name = window_name
    
    def run(self) -> None:
        """Run the main application loop."""
        print("🎥 Starting Face Recognition App...")
        print("📌 Press 'q' to quit")
        print("=" * 60)
        
        if not self.camera.is_opened():
            print("❌ Camera is not opened!")
            return
        
        try:
            while True:
                # Read frame
                ret, frame = self.camera.read()
                
                if not ret:
                    print("❌ Failed to read frame from camera")
                    break
                
                # Recognize faces
                result = self.recognize_usecase.execute(frame)
                
                # Draw results on frame
                display_frame = self._draw_results(frame, result)
                
                # Show frame
                try:
                    cv2.imshow(self.window_name, display_frame)
                except cv2.error as e:
                    print(f"\n❌ OpenCV GUI Error: {e}")
                    print("💡 OpenCV không hỗ trợ GUI trên hệ thống này")
                    print("📊 Dùng Dashboard thay thế: streamlit run dashboard.py")
                    break
                
                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Quitting...")
                    break
                elif key == ord('r'):
                    # Hot reload known faces
                    print("\n🔄 Reloading known faces...")
                    self.recognize_usecase.load_known_usecase.reload()
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        
        finally:
            # Cleanup
            self.camera.release()
            try:
                cv2.destroyAllWindows()
            except:
                pass  # Ignore OpenCV cleanup errors on Windows
            print("✅ Camera released and windows closed")
    
    def _draw_results(self, frame: np.ndarray, result: RecognitionResult) -> np.ndarray:
        """
        Draw recognition results on frame.
        
        Args:
            frame: Original BGR frame
            result: Recognition result
            
        Returns:
            Frame with drawings
        """
        display_frame = frame.copy()
        
        # Draw info header
        info_text = f"Faces: {len(result.faces)} | Press 'q' to quit, 'r' to reload"
        cv2.putText(
            display_frame, 
            info_text,
            (10, 25),
            FONT,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Draw each detected face
        for face in result.faces:
            box = face.box
            
            # Draw bounding box
            color = face.color
            cv2.rectangle(
                display_frame,
                (box.left, box.top),
                (box.right, box.bottom),
                color,
                BBOX_THICKNESS
            )
            
            # Draw label background
            label = face.label
            label_y = box.top - 10 if box.top > 30 else box.bottom + 20
            
            # Get text size for background
            (text_width, text_height), baseline = cv2.getTextSize(
                label, FONT, FONT_SCALE, FONT_THICKNESS
            )
            
            # Draw filled rectangle for text background
            cv2.rectangle(
                display_frame,
                (box.left, label_y - text_height - 5),
                (box.left + text_width + 5, label_y + 5),
                color,
                -1  # Filled
            )
            
            # Draw text
            cv2.putText(
                display_frame,
                label,
                (box.left + 2, label_y),
                FONT,
                FONT_SCALE,
                (255, 255, 255),  # White text
                FONT_THICKNESS
            )
            
            # Draw distance (for debugging)
            if face.distance < 1.0:
                distance_text = f"{face.distance:.2f}"
                cv2.putText(
                    display_frame,
                    distance_text,
                    (box.left, box.bottom + 15),
                    FONT,
                    0.4,
                    color,
                    1
                )
        
        return display_frame
