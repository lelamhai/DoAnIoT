"""
Pytest Configuration & Fixtures
Shared test fixtures and configuration for all tests
"""

import pytest
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from backend.core.models import MotionEvent, MotionStatus, PredictionResult, PredictionLabel, AlertLevel
from backend.infrastructure.database import Database


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create temporary database path for testing"""
    db_dir = tmp_path_factory.mktemp("data")
    return str(db_dir / "test_security.db")


@pytest.fixture
def database(test_db_path):
    """Create test database instance"""
    db = Database(test_db_path)
    yield db
    db.close()
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def sample_motion_event():
    """Sample MotionEvent for testing"""
    return MotionEvent(
        timestamp=datetime(2026, 1, 6, 14, 30, 0),
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="TEST_SENSOR_001",
        location="test_room"
    )


@pytest.fixture
def sample_no_motion_event():
    """Sample no-motion event"""
    return MotionEvent(
        timestamp=datetime(2026, 1, 6, 14, 31, 0),
        motion=MotionStatus.NO_MOTION,
        sensor_id="TEST_SENSOR_001",
        location="test_room"
    )


@pytest.fixture
def sample_prediction_normal():
    """Sample normal prediction result"""
    event = MotionEvent(
        timestamp=datetime(2026, 1, 6, 14, 0, 0),
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="TEST_001",
        location="test"
    )
    
    return PredictionResult(
        timestamp=datetime(2026, 1, 6, 14, 0, 0),
        motion_event=event,
        prediction_label=PredictionLabel.NORMAL,
        confidence=0.85,
        alert_level=AlertLevel.SAFE,
        features={
            'hour': 14,
            'day_of_week': 0,
            'is_night': 0,
            'frequency_5min': 3,
            'duration': 2
        }
    )


@pytest.fixture
def sample_prediction_suspicious():
    """Sample suspicious prediction result"""
    event = MotionEvent(
        timestamp=datetime(2026, 1, 6, 2, 0, 0),
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="TEST_001",
        location="test"
    )
    
    return PredictionResult(
        timestamp=datetime(2026, 1, 6, 2, 0, 0),
        motion_event=event,
        prediction_label=PredictionLabel.SUSPICIOUS,
        confidence=0.92,
        alert_level=AlertLevel.CRITICAL,
        features={
            'hour': 2,
            'day_of_week': 0,
            'is_night': 1,
            'frequency_5min': 5,
            'duration': 4
        }
    )


@pytest.fixture
def mqtt_payload_valid():
    """Valid MQTT payload"""
    return {
        "timestamp": "2026-01-06T14:30:00",
        "motion": 1,
        "sensor_id": "TEST_SENSOR_001",
        "location": "test_room"
    }


@pytest.fixture
def mqtt_payload_invalid():
    """Invalid MQTT payload (missing required fields)"""
    return {
        "sensor_id": "TEST_SENSOR_001",
        "location": "test_room"
        # Missing: timestamp, motion
    }


@pytest.fixture
def temp_csv_file(tmp_path):
    """Temporary CSV file for testing"""
    csv_file = tmp_path / "test_events.csv"
    return str(csv_file)


@pytest.fixture
def mock_model_path(tmp_path):
    """Mock AI model path"""
    import joblib
    from sklearn.ensemble import RandomForestClassifier
    
    # Create simple model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    
    # Train with dummy data
    import numpy as np
    X = np.random.rand(100, 6)
    y = np.random.randint(0, 2, 100)
    model.fit(X, y)
    
    # Save to temp path
    model_path = tmp_path / "test_classifier.pkl"
    joblib.dump(model, model_path)
    
    return str(model_path)


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # Reset ConfigManager singleton if exists
    from backend.infrastructure.config import ConfigManager
    ConfigManager._instance = None
    ConfigManager._config = None
    
    yield
    
    # Cleanup after test
    ConfigManager._instance = None
    ConfigManager._config = None


# Hooks
def pytest_configure(config):
    """Pytest configuration hook"""
    print("\n🧪 Starting IoT Security System Tests")
    print("=" * 70)


def pytest_sessionfinish(session, exitstatus):
    """Pytest session finish hook"""
    print("\n" + "=" * 70)
    print("✅ Testing session completed")
    print(f"Exit status: {exitstatus}")
