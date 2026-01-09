"""FastAPI service for Face Recognition."""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import base64
import cv2
import numpy as np

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from face_app.config.settings import DB_PATH, TOLERANCE
from face_app.infrastructure.face_engines.fr_dlib_engine import FRDlibEngine
from face_app.infrastructure.repos.filesystem_known_repo import FilesystemKnownRepo
from face_app.infrastructure.repos.sqlite_recognition_repo import SQLiteRecognitionRepo
from face_app.domain.policies import MatchPolicy
from face_app.application.usecases.load_known_faces import LoadKnownFacesUseCase
from face_app.application.usecases.recognize_frame import RecognizeFrameUseCase
from api.models import (
    RecognitionEventResponse,
    RecognitionStatsResponse,
    RecognizeRequest,
    RecognizeResponse,
    FaceDetectionResponse
)

# Initialize FastAPI
app = FastAPI(
    title="Face Recognition API",
    description="RESTful API for face recognition system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components (lazy loading)
_face_engine = None
_recognize_usecase = None


def get_recognize_usecase():
    """Get or initialize recognize use case."""
    global _face_engine, _recognize_usecase
    
    if _recognize_usecase is None:
        # Initialize infrastructure
        _face_engine = FRDlibEngine()
        known_repo = FilesystemKnownRepo()
        recognition_repo = SQLiteRecognitionRepo()
        
        # Initialize domain
        match_policy = MatchPolicy(tolerance=TOLERANCE)
        
        # Initialize application
        load_known_usecase = LoadKnownFacesUseCase(known_repo)
        load_known_usecase.execute()  # Load known faces
        
        _recognize_usecase = RecognizeFrameUseCase(
            face_engine=_face_engine,
            load_known_usecase=load_known_usecase,
            recognition_repo=recognition_repo,
            match_policy=match_policy
        )
    
    return _recognize_usecase


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Face Recognition API",
        "version": "1.0.0",
        "endpoints": {
            "GET /events": "Get recognition events",
            "GET /stats": "Get statistics",
            "POST /recognize": "Recognize faces in image",
            "POST /recognize/upload": "Recognize faces from uploaded file"
        }
    }


@app.get("/events", response_model=List[RecognitionEventResponse])
def get_events(limit: int = 100, name: Optional[str] = None):
    """
    Get recognition events from database.
    
    Args:
        limit: Maximum number of events to return
        name: Filter by person name (optional)
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        if name:
            query = "SELECT id, name, time FROM recognitions WHERE name = ? ORDER BY id DESC LIMIT ?"
            cursor.execute(query, (name, limit))
        else:
            query = "SELECT id, name, time FROM recognitions ORDER BY id DESC LIMIT ?"
            cursor.execute(query, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            RecognitionEventResponse(id=r[0], name=r[1], time=r[2])
            for r in results
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/stats", response_model=RecognitionStatsResponse)
def get_statistics():
    """Get recognition statistics."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM recognitions")
        total = cursor.fetchone()[0]
        
        # Unique people
        cursor.execute("SELECT COUNT(DISTINCT name) FROM recognitions")
        unique_people = cursor.fetchone()[0]
        
        # Today's events
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM recognitions WHERE time LIKE ?", (f"{today}%",))
        today_count = cursor.fetchone()[0]
        
        # Most frequent person
        cursor.execute("""
            SELECT name, COUNT(*) as count 
            FROM recognitions 
            GROUP BY name 
            ORDER BY count DESC 
            LIMIT 1
        """)
        most_frequent = cursor.fetchone()
        
        conn.close()
        
        return RecognitionStatsResponse(
            total_events=total,
            unique_people=unique_people,
            today_events=today_count,
            most_frequent_person=most_frequent[0] if most_frequent else None,
            most_frequent_count=most_frequent[1] if most_frequent else None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/recognize", response_model=RecognizeResponse)
def recognize_image(request: RecognizeRequest):
    """
    Recognize faces in a base64-encoded image.
    
    Args:
        request: RecognizeRequest with base64 image
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Get recognize use case
        usecase = get_recognize_usecase()
        
        # Recognize faces
        result = usecase.execute(frame)
        
        # Convert to response
        faces = [
            FaceDetectionResponse(
                name=face.name,
                is_known=face.is_known,
                distance=face.distance,
                box={
                    "top": face.box.top,
                    "right": face.box.right,
                    "bottom": face.box.bottom,
                    "left": face.box.left
                }
            )
            for face in result.faces
        ]
        
        return RecognizeResponse(
            success=True,
            faces=faces,
            processed_at=datetime.now().isoformat(),
            message=f"Detected {len(faces)} face(s)"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")


@app.post("/recognize/upload", response_model=RecognizeResponse)
async def recognize_upload(file: UploadFile = File(...)):
    """
    Recognize faces from uploaded image file.
    
    Args:
        file: Uploaded image file
    """
    try:
        # Read file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Get recognize use case
        usecase = get_recognize_usecase()
        
        # Recognize faces
        result = usecase.execute(frame)
        
        # Convert to response
        faces = [
            FaceDetectionResponse(
                name=face.name,
                is_known=face.is_known,
                distance=face.distance,
                box={
                    "top": face.box.top,
                    "right": face.box.right,
                    "bottom": face.box.bottom,
                    "left": face.box.left
                }
            )
            for face in result.faces
        ]
        
        return RecognizeResponse(
            success=True,
            faces=faces,
            processed_at=datetime.now().isoformat(),
            message=f"Detected {len(faces)} face(s)"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")


@app.post("/reload")
def reload_known_faces():
    """Reload known faces from dataset."""
    try:
        usecase = get_recognize_usecase()
        encodings, names = usecase.load_known_usecase.reload()
        
        return {
            "success": True,
            "message": f"Reloaded {len(encodings)} face encodings from {len(set(names))} people"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
