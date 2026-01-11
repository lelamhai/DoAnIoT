"""Main entry point for Face Recognition App."""
from datetime import datetime
from face_app.infrastructure.camera.opencv_camera import OpenCVCamera
from face_app.infrastructure.face_engines.fr_dlib_engine import FRDlibEngine
from face_app.infrastructure.repos.filesystem_known_repo import FilesystemKnownRepo
from face_app.infrastructure.repos.sqlite_recognition_repo import SQLiteRecognitionRepo
from face_app.infrastructure.monitoring.stranger_monitor import StrangerMonitor
from face_app.infrastructure.notifications.email_service import EmailNotificationService
from face_app.domain.policies import MatchPolicy
from face_app.application.usecases.load_known_faces import LoadKnownFacesUseCase
from face_app.application.usecases.recognize_frame import RecognizeFrameUseCase
from face_app.presentation.opencv_app import OpenCVApp
from face_app.config import settings


def main():
    """Initialize and run the face recognition app."""
    print("=" * 60)
    print("🚀 Face Recognition Camera App")
    print("=" * 60)
    
    try:
        # Initialize infrastructure (adapters)
        print("\n📦 Initializing components...")
        
        face_engine = FRDlibEngine()
        print("   ✅ Face engine initialized")
        
        known_repo = FilesystemKnownRepo()
        recognition_repo = SQLiteRecognitionRepo()
        print("   ✅ Repositories initialized")
        
        # Initialize domain
        match_policy = MatchPolicy(tolerance=settings.TOLERANCE)
        print(f"   ✅ Match policy initialized (tolerance={settings.TOLERANCE})")
        
        # Initialize email service for stranger alerts
        email_service = None
        if settings.ENABLE_STRANGER_ALERTS:
            if settings.SENDER_EMAIL and settings.RECIPIENT_EMAILS[0]:
                email_service = EmailNotificationService(
                    smtp_server=settings.SMTP_SERVER,
                    smtp_port=settings.SMTP_PORT,
                    sender_email=settings.SENDER_EMAIL,
                    sender_password=settings.SENDER_PASSWORD,
                    recipient_emails=settings.RECIPIENT_EMAILS,
                    enabled=True
                )
                print(f"   ✅ Email alerts enabled → {', '.join(settings.RECIPIENT_EMAILS)}")
            else:
                print("   ⚠️  Email alerts enabled but credentials not configured!")
                print("   💡 Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAILS")
        
        # Initialize stranger monitor with email callback
        stranger_monitor = None
        if settings.ENABLE_STRANGER_ALERTS and email_service:
            def on_stranger_alert(count: int, timestamp: datetime):
                """Callback when stranger threshold exceeded."""
                print(f"\n🚨 CẢNH BÁO: Phát hiện {count} người lạ trong {settings.STRANGER_TIME_WINDOW}s!")
                email_service.send_stranger_alert(count, timestamp)
            
            stranger_monitor = StrangerMonitor(
                time_window_seconds=settings.STRANGER_TIME_WINDOW,
                threshold=settings.STRANGER_THRESHOLD,
                alert_callback=on_stranger_alert,
                alert_cooldown_seconds=settings.STRANGER_ALERT_COOLDOWN
            )
            print(f"   ✅ Stranger monitor: {settings.STRANGER_THRESHOLD} detections/{settings.STRANGER_TIME_WINDOW}s")
        
        # Initialize application (use cases)
        load_known_usecase = LoadKnownFacesUseCase(known_repo)
        print("   ✅ Use cases initialized")
        
        # Load known faces
        print("\n" + "=" * 60)
        encodings, names = load_known_usecase.execute()
        print("=" * 60)
        
        if not encodings:
            print("\n⚠️  WARNING: No known faces loaded!")
            print("💡 Add images to known_faces/<name>/ folders")
            print("📖 See known_faces/README.md for instructions\n")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("👋 Exiting...")
                return
        
        recognize_usecase = RecognizeFrameUseCase(
            face_engine=face_engine,
            load_known_usecase=load_known_usecase,
            recognition_repo=recognition_repo,
            match_policy=match_policy,
            stranger_monitor=stranger_monitor
        )
        
        # Initialize camera
        print("\n📷 Opening camera...")
        camera = OpenCVCamera()
        print("   ✅ Camera opened successfully")
        
        # Initialize presentation with stranger monitor
        app = OpenCVApp(camera, recognize_usecase, stranger_monitor=stranger_monitor)
        
        # Run app
        print("\n" + "=" * 60)
        app.run()
        
    except RuntimeError as e:
        print(f"\n❌ Runtime Error: {e}")
        print("💡 Make sure your camera is connected and not in use by another app")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("👋 Face Recognition App terminated")
    print("=" * 60)


if __name__ == "__main__":
    main()
