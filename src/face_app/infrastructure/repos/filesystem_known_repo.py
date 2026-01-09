"""Filesystem repository for loading known faces dataset."""
from typing import List, Tuple
from pathlib import Path
import numpy as np
import face_recognition
from PIL import Image
from face_app.domain.ports import KnownFaceRepoPort
from face_app.config.settings import KNOWN_FACES_DIR, MODEL


class FilesystemKnownRepo(KnownFaceRepoPort):
    """Load known faces from filesystem (known_faces/<name>/*.jpg)."""
    
    def __init__(self, dataset_path: Path = KNOWN_FACES_DIR, model: str = MODEL):
        """
        Initialize repository.
        
        Args:
            dataset_path: Path to known_faces directory
            model: Face detection model for encoding
        """
        self.dataset_path = dataset_path
        self.model = model
    
    def load_known_faces(self) -> Tuple[List[np.ndarray], List[str]]:
        """
        Load all known faces from dataset.
        
        Directory structure:
            known_faces/
                Person1/
                    01.jpg
                    02.jpg
                Person2/
                    01.jpg
        
        Returns:
            (encodings, names) - lists of same length
        """
        known_encodings = []
        known_names = []
        
        if not self.dataset_path.exists():
            print(f"⚠️  Dataset path not found: {self.dataset_path}")
            return [], []
        
        # Iterate through each person's folder
        person_folders = [f for f in self.dataset_path.iterdir() if f.is_dir()]
        
        if not person_folders:
            print(f"⚠️  No person folders found in {self.dataset_path}")
            print(f"💡 Create folders like: known_faces/YourName/")
            return [], []
        
        print(f"📂 Loading known faces from {self.dataset_path}...")
        
        for person_folder in person_folders:
            person_name = person_folder.name
            
            # Get all image files
            image_files = list(person_folder.glob("*.jpg")) + \
                         list(person_folder.glob("*.jpeg")) + \
                         list(person_folder.glob("*.png"))
            
            if not image_files:
                print(f"⚠️  No images found for {person_name}")
                continue
            
            print(f"   Loading {person_name} ({len(image_files)} images)...", end=" ")
            
            person_encodings_count = 0
            
            # Process each image
            for image_path in image_files:
                try:
                    # Load image
                    image = face_recognition.load_image_file(str(image_path))
                    
                    # Get face encodings
                    encodings = face_recognition.face_encodings(image, model=self.model)
                    
                    if encodings:
                        # Use the first detected face
                        known_encodings.append(encodings[0])
                        known_names.append(person_name)
                        person_encodings_count += 1
                    else:
                        print(f"\n      ⚠️  No face detected in {image_path.name}")
                
                except Exception as e:
                    print(f"\n      ❌ Error loading {image_path.name}: {e}")
            
            print(f"✅ {person_encodings_count} faces loaded")
        
        print(f"\n✅ Total: {len(known_encodings)} face encodings from {len(set(known_names))} people\n")
        
        return known_encodings, known_names
