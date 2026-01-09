"""
Test Camera - Kiểm tra camera hoạt động
Chạy: python test_camera.py
Nhấn 'q' để thoát
"""
import cv2

def test_camera():
    """Test xem camera có hoạt động không."""
    print("🎥 Đang mở camera...")
    print("📌 Nhấn 'q' để thoát")
    
    # Mở camera (index 0 = camera mặc định)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Không thể mở camera!")
        print("💡 Hãy kiểm tra:")
        print("   - Camera có được kết nối không?")
        print("   - Ứng dụng khác có đang dùng camera không?")
        print("   - Quyền truy cập camera đã được cấp chưa?")
        return
    
    print("✅ Camera đã sẵn sàng!")
    
    while True:
        # Đọc frame từ camera
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Không thể đọc frame từ camera")
            break
        
        # Hiển thị thông tin
        height, width = frame.shape[:2]
        info_text = f"Resolution: {width}x{height} | Press 'q' to quit"
        cv2.putText(frame, info_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Hiển thị frame
        cv2.imshow('Camera Test - Face Recognition App', frame)
        
        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Đang đóng camera...")
            break
    
    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Camera đã đóng thành công!")

if __name__ == "__main__":
    test_camera()
