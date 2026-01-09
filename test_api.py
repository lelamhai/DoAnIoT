"""Test API client for Face Recognition API."""
import requests
import base64
from pathlib import Path

API_URL = "http://localhost:8000"


def test_root():
    """Test root endpoint."""
    response = requests.get(f"{API_URL}/")
    print("GET /")
    print(response.json())
    print()


def test_stats():
    """Test statistics endpoint."""
    response = requests.get(f"{API_URL}/stats")
    print("GET /stats")
    print(response.json())
    print()


def test_events():
    """Test events endpoint."""
    response = requests.get(f"{API_URL}/events?limit=10")
    print("GET /events?limit=10")
    events = response.json()
    for event in events[:5]:  # Show first 5
        print(f"  {event['id']}: {event['name']} at {event['time']}")
    print()


def test_recognize_upload(image_path: str):
    """Test recognize endpoint with file upload."""
    if not Path(image_path).exists():
        print(f"Image not found: {image_path}")
        return
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_URL}/recognize/upload", files=files)
    
    print(f"POST /recognize/upload (image: {image_path})")
    result = response.json()
    
    if result['success']:
        print(f"  Detected {len(result['faces'])} face(s):")
        for face in result['faces']:
            print(f"    - {face['name']} (known: {face['is_known']}, distance: {face['distance']:.3f})")
    else:
        print(f"  Error: {result.get('message')}")
    print()


def test_reload():
    """Test reload endpoint."""
    response = requests.post(f"{API_URL}/reload")
    print("POST /reload")
    print(response.json())
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Face Recognition API Test Client")
    print("=" * 60)
    print()
    
    # Test endpoints
    test_root()
    test_stats()
    test_events()
    
    # Test recognition with sample image
    # Uncomment and provide your test image path
    # test_recognize_upload("known_faces/Linh/1.jpg")
    
    # Test reload
    # test_reload()
    
    print("=" * 60)
    print("Done!")
