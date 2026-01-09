"""Advanced main entry point with Phase 4 features."""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from face_app.config import settings

# Choose components based on config
if settings.USE_INSIGHTFACE:
    from face_app.infrastructure.face_engines.insightface_engine import InsightFaceEngine
    FaceEngine = InsightFaceEngine
    engine_kwargs = {
        'model_name': settings.INSIGHTFACE_MODEL,
        'ctx_id': settings.INSIGHTFACE_CTX_ID
    }
else:
    from face_app.infrastructure.face_engines.fr_dlib_engine import FRDlibEngine
    FaceEngine = FRDlibEngine
    engine_kwargs = {}

if settings.USE_THREADED_CAMERA:
    from face_app.infrastructure.camera.threaded_camera import ThreadedCamera
    Camera = ThreadedCamera
    camera_kwargs = {'buffer_size': settings.CAMERA_BUFFER_SIZE}
else:
    from face_app.infrastructure.camera.opencv_camera import OpenCVCamera
    Camera = OpenCVCamera
    camera_kwargs = {}

from face_app.infrastructure.repos.sqlite_recognition_repo import SQLiteRecognitionRepo

# Choose repo based on engine
if settings.USE_INSIGHTFACE:
    from face_app.infrastructure.repos.insightface_known_repo import InsightFaceKnownRepo
    KnownRepo = InsightFaceKnownRepo
else:
    from face_app.infrastructure.repos.filesystem_known_repo import FilesystemKnownRepo
    KnownRepo = FilesystemKnownRepo
from face_app.domain.policies import MatchPolicy
from face_app.application.usecases.load_known_faces import LoadKnownFacesUseCase
from face_app.application.usecases.recognize_frame import RecognizeFrameUseCase
from face_app.presentation.opencv_app import OpenCVApp


def main():
    """Initialize and run the advanced face recognition app."""
    print("=" * 70)
    print("🚀 Face Recognition Camera App - Advanced Mode (Phase 4)")
    print("=" * 70)
    
    # Show configuration
    print("\n⚙️  Configuration:")
    print(f"   Engine: {'InsightFace' if settings.USE_INSIGHTFACE else 'face_recognition (dlib)'}")
    print(f"   Tracking: {'Enabled' if settings.ENABLE_TRACKING else 'Disabled'}")
    print(f"   Threaded Camera: {'Enabled' if settings.USE_THREADED_CAMERA else 'Disabled'}")
    print(f"   Anti-spoofing: {'Enabled' if settings.ENABLE_ANTISPOOFING else 'Disabled'}")
    print(f"   Tolerance: {settings.TOLERANCE}")
    
    try:
        # Initialize infrastructure (adapters)
        print("\n📦 Initializing components...")
        
        face_engine = FaceEngine(**engine_kwargs)
        print("   ✅ Face engine initialized")
        
        known_repo = KnownRepo()
        recognition_repo = SQLiteRecognitionRepo()
        print("   ✅ Repositories initialized")
        
        # Initialize domain
        match_policy = MatchPolicy(tolerance=settings.TOLERANCE)
        print(f"   ✅ Match policy initialized")
        
        # Initialize application (use cases)
        load_known_usecase = LoadKnownFacesUseCase(known_repo)
        print("   ✅ Use cases initialized")
        
        # Load known faces
        print("\n" + "=" * 70)
        encodings, names = load_known_usecase.execute()
        print("=" * 70)
        
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
            match_policy=match_policy
        )
        
        # Initialize camera
        print(f"\n📷 Opening camera (threaded: {settings.USE_THREADED_CAMERA})...")
        camera = Camera(settings.CAMERA_INDEX, **camera_kwargs)
        print("   ✅ Camera opened successfully")
        
        # Initialize presentation
        app = OpenCVApp(camera, recognize_usecase)
        
        # Run app
        print("\n" + "=" * 70)
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
    
    print("\n" + "=" * 70)
    print("👋 Face Recognition App terminated")
    print("=" * 70)


if __name__ == "__main__":
    main()
