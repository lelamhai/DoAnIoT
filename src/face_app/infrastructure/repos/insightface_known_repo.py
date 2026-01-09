"""Filesystem repository for loading known faces using InsightFace."""
from typing import List, Tuple
from pathlib import Path
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from face_app.domain.ports import KnownFaceRepoPort
from face_app.config.settings import KNOWN_FACES_DIR, INSIGHTFACE_MODEL, INSIGHTFACE_CTX_ID


class InsightFaceKnownRepo(KnownFaceRepoPort):
    """Load known faces from filesystem using InsightFace."""
    
    def __init__(
        self, 
        dataset_path: Path = KNOWN_FACES_DIR,
        model_name: str = INSIGHTFACE_MODEL,
        ctx_id: int = INSIGHTFACE_CTX_ID
    ):
        """
        Initialize repository with InsightFace.
        
        Args:
            dataset_path: Path to known_faces directory
            model_name: InsightFace model name
            ctx_id: Device ID (-1 for CPU)
        """
        self.dataset_path = dataset_path
        self.app = FaceAnalysis(
            name=model_name,
            providers=['CPUExecutionProvider'] if ctx_id == -1 else ['CUDAExecutionProvider']
        )
        self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))
    
    def load_known_faces(self) -> Tuple[List[np.ndarray], List[str]]:
        """
        Load all known faces from dataset using InsightFace.
        
        Returns:
            (encodings, names) - lists of same length
        """
        known_encodings = []
        known_names = []
        
        if not self.dataset_path.exists():
            print(f"⚠️  Dataset path not found: {self.dataset_path}")
            return [], []
        
        person_folders = [f for f in self.dataset_path.iterdir() if f.is_dir()]
        
        if not person_folders:
            print(f"⚠️  No person folders found in {self.dataset_path}")
            return [], []
        
        print(f"📂 Loading known faces from {self.dataset_path}...")
        
        for person_folder in person_folders:
            person_name = person_folder.name
            
            image_files = list(person_folder.glob("*.jpg")) + \
                         list(person_folder.glob("*.jpeg")) + \
                         list(person_folder.glob("*.png"))
            
            if not image_files:
                print(f"⚠️  No images found for {person_name}")
                continue
            
            print(f"   Loading {person_name} ({len(image_files)} images)...", end=" ")
            
            person_encodings_count = 0
            
            for image_path in image_files:
                try:
                    # Load image with OpenCV (BGR)
                    image = cv2.imread(str(image_path))
                    if image is None:
                        print(f"\n      ⚠️  Cannot read {image_path.name}")
                        continue
                    
                    # Get faces with InsightFace
                    faces = self.app.get(image)
                    
                    if faces:
                        # Use the first detected face
                        known_encodings.append(faces[0].embedding)
                        known_names.append(person_name)
                        person_encodings_count += 1
                    else:
                        print(f"\n      ⚠️  No face detected in {image_path.name}")
                
                except Exception as e:
                    print(f"\n      ❌ Error loading {image_path.name}: {e}")
            
            print(f"✅ {person_encodings_count} faces loaded")
        
        print(f"\n✅ Total: {len(known_encodings)} face encodings from {len(set(known_names))} people\n")
        
        return known_encodings, known_names
