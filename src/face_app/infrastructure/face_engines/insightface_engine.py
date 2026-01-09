"""InsightFace engine adapter - More accurate and faster than dlib."""
from typing import List
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from face_app.domain.ports import FaceEnginePort
from face_app.domain.entities import BoundingBox


class InsightFaceEngine(FaceEnginePort):
    """Adapter for InsightFace library - high accuracy face recognition."""
    
    def __init__(self, model_name: str = 'buffalo_l', ctx_id: int = -1):
        """
        Initialize InsightFace engine.
        
        Args:
            model_name: Model name ('buffalo_l' recommended for accuracy, 'buffalo_s' for speed)
            ctx_id: -1 for CPU, 0+ for GPU device ID
        """
        self.app = FaceAnalysis(name=model_name, providers=['CPUExecutionProvider'] if ctx_id == -1 else ['CUDAExecutionProvider'])
        self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))
        self.ctx_id = ctx_id
        print(f"✅ InsightFace initialized (model: {model_name}, device: {'CPU' if ctx_id == -1 else f'GPU:{ctx_id}'})")
    
    def detect_faces(self, rgb_frame: np.ndarray) -> List[BoundingBox]:
        """
        Detect faces in an RGB frame.
        
        Args:
            rgb_frame: RGB image as numpy array
            
        Returns:
            List of BoundingBox objects
        """
        # InsightFace expects BGR
        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        # Get faces
        faces = self.app.get(bgr_frame)
        
        # Convert to BoundingBox
        boxes = []
        for face in faces:
            bbox = face.bbox.astype(int)
            # bbox format: [x1, y1, x2, y2]
            boxes.append(BoundingBox(
                top=bbox[1],
                right=bbox[2],
                bottom=bbox[3],
                left=bbox[0]
            ))
        
        return boxes
    
    def encode_faces(self, rgb_frame: np.ndarray, boxes: List[BoundingBox]) -> List[np.ndarray]:
        """
        Generate face encodings for detected faces.
        
        Args:
            rgb_frame: RGB image as numpy array
            boxes: List of BoundingBox for detected faces
            
        Returns:
            List of 512-dimensional face embeddings (InsightFace standard)
        """
        # InsightFace expects BGR
        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        # Get all faces with embeddings
        faces = self.app.get(bgr_frame)
        
        # Extract embeddings (already computed by InsightFace)
        encodings = [face.embedding for face in faces[:len(boxes)]]
        
        return encodings
    
    def compute_distances(self, known_encodings: List[np.ndarray], probe_encoding: np.ndarray) -> List[float]:
        """
        Compute distances between known encodings and a probe encoding.
        Uses cosine distance (1 - cosine_similarity).
        
        Args:
            known_encodings: List of known face encodings
            probe_encoding: Encoding of the face to match
            
        Returns:
            List of distances (lower = more similar)
        """
        if not known_encodings:
            return []
        
        # Compute cosine similarity
        similarities = []
        for known_enc in known_encodings:
            # Cosine similarity = dot(A, B) / (norm(A) * norm(B))
            similarity = np.dot(known_enc, probe_encoding) / (
                np.linalg.norm(known_enc) * np.linalg.norm(probe_encoding)
            )
            similarities.append(similarity)
        
        # Convert to distance (lower is better)
        distances = [1 - sim for sim in similarities]
        
        return distances
    
    def get_face_quality(self, rgb_frame: np.ndarray) -> List[dict]:
        """
        Get face quality metrics (bonus feature).
        
        Returns:
            List of dicts with quality info: {bbox, quality, landmark, age, gender}
        """
        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        faces = self.app.get(bgr_frame)
        
        results = []
        for face in faces:
            results.append({
                'bbox': face.bbox,
                'det_score': face.det_score,  # Detection confidence
                'landmark': face.landmark_2d_106 if hasattr(face, 'landmark_2d_106') else None,
                'age': face.age if hasattr(face, 'age') else None,
                'gender': face.gender if hasattr(face, 'gender') else None
            })
        
        return results
