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
        stranger_monitor=None,
        mqtt_client=None,
        window_name: str = "Face Recognition - Press 'q' to quit"
    ):
        """
        Initialize OpenCV app.
        
        Args:
            camera: Camera port
            recognize_usecase: Use case for recognizing frames
            stranger_monitor: Optional stranger detection monitor
            mqtt_client: Optional MQTT client for PIR sensor control
            window_name: Window title
        """
        self.camera = camera
        self.recognize_usecase = recognize_usecase
        self.stranger_monitor = stranger_monitor
        self.mqtt_client = mqtt_client
        self.window_name = window_name
        
        # Khởi tạo active: False nếu dùng MQTT (chờ PIR), True nếu manual mode
        self.active = False if mqtt_client else True
        
        # Setup MQTT callback to update active state from PIR
        if self.mqtt_client:
            def on_pir_message(payload: str):
                """Callback khi nhận message từ PIR sensor."""
                payload = payload.strip()
                if payload == "1":
                    self.active = True
                    print(f"\n🟢 PIR: Motion detected → ACTIVE = True (ghi DB + email)")
                elif payload == "0":
                    self.active = False
                    print(f"\n🔴 PIR: No motion → ACTIVE = False (chỉ hiển thị)")
                else:
                    print(f"\n⚠️  Unknown PIR message: '{payload}'")
            
            # Register callback (will be used when subscribing in main)
            self._pir_callback = on_pir_message
    
    def run(self) -> None:
        """Run the main application loop."""
        print("🎥 Starting Face Recognition App...")
        print("📌 Press 'q' to quit, 'r' to reload, 'a' to toggle ACTIVE mode")
        mqtt_status = "Connected" if (self.mqtt_client and self.mqtt_client.is_connected()) else "Disabled"
        print(f"📡 MQTT PIR Control: {mqtt_status}")
        print(f"📊 ACTIVE mode: {self.active} (BẬT = ghi DB/email, TẮT = chỉ hiển thị)")
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
                
                # Run face recognition (active controls DB/email logging)
                result = self.recognize_usecase.execute(frame, active=self.active)
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
                elif key == ord('a'):
                    # Toggle active mode
                    self.active = not self.active
                    status = "BẬT" if self.active else "TẮT"
                    print(f"\n🔄 ACTIVE mode: {status} (BẬT = ghi DB/email, TẮT = chỉ hiển thị)")
        
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
    
    def _draw_pir_inactive(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw PIR inactive status on frame (no face recognition).
        
        Args:
            frame: Original BGR frame
            
        Returns:
            Frame with PIR status message
        """
        display_frame = frame.copy()
        
        # Draw header
        info_text = "Press 'q' to quit, 'r' to reload"
        cv2.putText(
            display_frame, 
            info_text,
            (10, 25),
            FONT,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Draw PIR status - RED for inactive
        pir_text = "PIR: NO MOTION - Face Recognition DISABLED"
        cv2.putText(
            display_frame,
            pir_text,
            (10, 50),
            FONT,
            0.6,
            (0, 0, 255),  # Red
            2
        )
        
        # Draw center message
        h, w = frame.shape[:2]
        center_text = "Waiting for motion..."
        (text_width, text_height), _ = cv2.getTextSize(
            center_text, FONT, 1.0, 2
        )
        center_x = (w - text_width) // 2
        center_y = (h + text_height) // 2
        
        cv2.putText(
            display_frame,
            center_text,
            (center_x, center_y),
            FONT,
            1.0,
            (0, 0, 255),
            2
        )
        
        return display_frame
    
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
        info_text = f"Faces: {len(result.faces)} | Press 'q' to quit, 'r' to reload, 'a' to toggle"
        cv2.putText(
            display_frame, 
            info_text,
            (10, 25),
            FONT,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Draw MQTT and ACTIVE status
        y_offset = 50
        
        # MQTT status
        mqtt_connected = self.mqtt_client and self.mqtt_client.is_connected()
        mqtt_text = f"MQTT: {'Connected' if mqtt_connected else 'Disconnected'}"
        mqtt_color = (0, 255, 0) if mqtt_connected else (128, 128, 128)
        cv2.putText(
            display_frame,
            mqtt_text,
            (10, y_offset),
            FONT,
            0.5,
            mqtt_color,
            1
        )
        y_offset += 25
        
        # ACTIVE status (controlled by PIR or manual toggle)
        active_text = f"ACTIVE: {'ON' if self.active else 'OFF'} ({'DB+Email' if self.active else 'Display only'})"
        active_color = (0, 255, 0) if self.active else (0, 0, 255)
        cv2.putText(
            display_frame,
            active_text,
            (10, y_offset),
            FONT,
            0.5,
            active_color,
            2
        )
        y_offset += 25
        
        # Draw stranger monitor status if enabled
        if self.stranger_monitor:
            status = self.stranger_monitor.get_status()
            status_text = f"Strangers: {status['current_count']}/{status['threshold']}"
            status_color = (0, 0, 255) if status['current_count'] >= status['threshold'] * 0.7 else (255, 255, 255)
            cv2.putText(
                display_frame,
                status_text,
                (10, y_offset),
                FONT,
                0.5,
                status_color,
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
