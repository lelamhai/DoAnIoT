"""Quick Phase 4 Test"""
import sys
sys.path.insert(0, '.')

print("Testing Phase 4 Components...\n")

# Test 1: Database
print("[1/3] Testing Database...")
from backend.infrastructure.database import Database
from backend.core.models import MotionEvent
from backend.core.enums import MotionStatus

db = Database("data/test_p4.db")
event = MotionEvent(
    timestamp="2026-01-06T20:00:00Z",
    motion=MotionStatus.MOTION_DETECTED,
    sensor_id="TEST",
    location="test_room"
)
event_id = db.insert_event(event, "NORMAL", 0.9, "SAFE")
print(f"  ✓ Database OK - Event ID: {event_id}")
db.close()

# Test 2: CSV Logger  
print("\n[2/3] Testing CSV Logger...")
from backend.infrastructure.logger import CSVLogger
logger = CSVLogger("logs/test_p4")
success = logger.log_event(event, "NORMAL", 0.9, "SAFE")
print(f"  ✓ CSV Logger OK - Logged: {success}")

# Test 3: Config
print("\n[3/3] Testing Config...")
from backend.infrastructure.config import ConfigManager
mqtt_config = ConfigManager.load_mqtt_config()
print(f"  ✓ Config OK - Topic: {mqtt_config['mqtt']['topic']}")

print("\n✅ Phase 4 components working!\n")
