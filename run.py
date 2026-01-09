"""Run script for Face Recognition App."""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run main
from face_app.main import main

if __name__ == "__main__":
    main()
