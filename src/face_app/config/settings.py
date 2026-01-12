"""Configuration settings for Face Recognition App."""
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
KNOWN_FACES_DIR = BASE_DIR / "known_faces"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "attendance.sqlite"

# Camera settings
CAMERA_INDEX = 0  # 0 = default camera
FRAME_WIDTH = 640  # Resize width for faster processing
PROCESS_EVERY_N_FRAMES = 1  # Process every frame (1) or skip frames for performance

# Face Recognition settings
TOLERANCE = 0.5  # Lower = stricter (0.4-0.6 recommended)
MODEL = "hog"  # "hog" (faster, CPU) or "cnn" (accurate, GPU needed)

# Phase 4 - Advanced settings
USE_INSIGHTFACE = False  # True to use InsightFace (more accurate), False for face_recognition
INSIGHTFACE_MODEL = "buffalo_l"  # buffalo_l (accurate) or buffalo_s (fast)
INSIGHTFACE_CTX_ID = -1  # -1 for CPU, 0+ for GPU

# Tracking settings
ENABLE_TRACKING = False  # Enable face tracking to reduce compute
TRACK_DETECT_INTERVAL = 5  # Run full detection every N frames
TRACK_MAX_DISAPPEARED = 10  # Remove track after N frames without update
TRACK_IOU_THRESHOLD = 0.3  # IoU threshold for matching tracks

# Performance settings
USE_THREADED_CAMERA = False  # Use threaded camera for better FPS
CAMERA_BUFFER_SIZE = 2  # Frame buffer size for threaded camera

# Anti-spoofing settings
ENABLE_ANTISPOOFING = False  # Enable basic anti-spoofing
ANTISPOOFING_MOTION_THRESHOLD = 2.0  # Motion threshold for liveness
ANTISPOOFING_TEXTURE_THRESHOLD = 10.0  # Texture variance threshold

# Database settings
COOLDOWN_SECONDS = 10  # Minimum seconds between logging same person

# Detection Tracking Settings
ENABLE_DETECTION_TRACKING = True  # Enable detection tracking for all people

# Stranger Detection & Email Alert settings
ENABLE_STRANGER_ALERTS = True  # Enable stranger detection alerts
STRANGER_TIME_WINDOW = 60  # Time window in seconds (1 minute)
STRANGER_THRESHOLD = 10  # Number of stranger detections to trigger alert
STRANGER_ALERT_COOLDOWN = 60  # Cooldown between alerts (1 minute)

# Known Person Detection settings (separate from Stranger)
ENABLE_KNOWN_PERSON_TRACKING = True  # Enable tracking for known people
KNOWN_PERSON_TIME_WINDOW = 60  # Time window for known person detection (seconds)
KNOWN_PERSON_THRESHOLD = 10  # Number of detections needed to log to database (SAME as stranger)
KNOWN_PERSON_LOG_COOLDOWN = 0  # No cooldown for known person logging (managed by threshold)
# Note: Known people use detection tracking like strangers but with SAME threshold
# Stranger: 10 detections → email + DB (when active=True)
# Known Person: 10 detections → DB only (when active=True, no email)

# Email settings
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Gmail SMTP server
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # TLS port
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "leelamhair@gmail.com")  # Your email address
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "ctym wxnc eklc frzw")  # App Password (not regular password!)
RECIPIENT_EMAILS = os.getenv("RECIPIENT_EMAILS", "haill.k23dtcn426@stu.ptit.edu.vn").split(",") if os.getenv("RECIPIENT_EMAILS") else ["haill.k23dtcn426@stu.ptit.edu.vn"]  # Comma-separated emails

# Security note: Use App Passwords for Gmail!
# 1. Enable 2-Factor Authentication: https://myaccount.google.com/security
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Set environment variable: SENDER_PASSWORD=your_app_password

# UI settings
BBOX_COLOR_KNOWN = (0, 255, 0)  # Green for known faces
BBOX_COLOR_UNKNOWN = (0, 0, 255)  # Red for strangers
BBOX_THICKNESS = 2
FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.6
FONT_THICKNESS = 2

# IoT / MQTT settings
ENABLE_PIR_CONTROL = True  # Enable PIR sensor control via MQTT
MQTT_BROKER = "broker.hivemq.com"  # Public MQTT broker
MQTT_PORT = 1883  # Default MQTT port
MQTT_CLIENT_ID = "face_recognition_app_nhom03"  # Unique client ID
MQTT_TOPIC_PIR = "iot/nhom03/security/pir"  # PIR sensor topic
MQTT_TOPIC_BUZZER = "iot/nhom03/security/buzzer"  # Buzzer/Speaker control topic
MQTT_KEEPALIVE = 60  # Keepalive interval in seconds

# Buzzer settings
BUZZER_DURATION = 5  # Auto tắt loa sau 5 giây

# Ensure directories exist
KNOWN_FACES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
