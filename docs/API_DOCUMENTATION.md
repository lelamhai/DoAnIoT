# 📖 API DOCUMENTATION

## IoT Security Monitoring System API Reference

---

## Backend Services API

### 1. MQTT Service

#### Class: `MQTTService`

**Purpose:** Manage MQTT connections, pub/sub operations

**Methods:**

```python
MQTTService(config: MQTTConfig)
```
- **Parameters:**
  - `config`: MQTT configuration object
- **Returns:** MQTTService instance

```python
connect() -> None
```
- **Purpose:** Connect to MQTT broker
- **Raises:** ConnectionError if broker unreachable

```python
subscribe(callback: Callable) -> None
```
- **Parameters:**
  - `callback`: Function to call on message received
- **Purpose:** Subscribe to configured topic

```python
publish(payload: dict) -> bool
```
- **Parameters:**
  - `payload`: JSON dictionary to publish
- **Returns:** True if successful

```python
disconnect() -> None
```
- **Purpose:** Clean disconnect from broker

**Example Usage:**
```python
from backend.services.mqtt_service import MQTTService
from backend.infrastructure.config import MQTTConfig

config = MQTTConfig(
    broker="test.mosquitto.org",
    port=1883,
    topic="iot/security/pir/nhom03"
)

mqtt = MQTTService(config)
mqtt.connect()

def on_message(payload):
    print(f"Received: {payload}")

mqtt.subscribe(callback=on_message)
```

---

### 2. Data Processor

#### Class: `DataProcessor`

**Purpose:** Validate and transform MQTT payloads

**Methods:**

```python
@staticmethod
validate_payload(payload: dict) -> bool
```
- **Parameters:**
  - `payload`: Dictionary from MQTT message
- **Returns:** True if valid
- **Required fields:** `timestamp`, `motion`

```python
@staticmethod
transform_to_event(payload: dict) -> Optional[MotionEvent]
```
- **Parameters:**
  - `payload`: Validated dictionary
- **Returns:** MotionEvent object or None
- **Transforms:** JSON → MotionEvent dataclass

**Example Usage:**
```python
from backend.services.data_processor import DataProcessor

payload = {
    "timestamp": "2026-01-06T14:30:00",
    "motion": 1,
    "sensor_id": "PIR_001",
    "location": "living_room"
}

if DataProcessor.validate_payload(payload):
    event = DataProcessor.transform_to_event(payload)
    print(event.motion)  # MotionStatus.MOTION_DETECTED
```

---

### 3. AI Service

#### Class: `AIService`

**Purpose:** AI-based motion classification

**Methods:**

```python
AIService(model_path: str = "ai_model/models/classifier.pkl")
```
- **Parameters:**
  - `model_path`: Path to trained model
- **Raises:** FileNotFoundError if model missing

```python
predict(event: MotionEvent, history: List[MotionEvent] = []) -> PredictionResult
```
- **Parameters:**
  - `event`: Current motion event
  - `history`: Previous events for context
- **Returns:** PredictionResult with label, confidence, alert level

**PredictionResult Fields:**
- `prediction_label`: NORMAL or SUSPICIOUS
- `confidence`: 0.0 - 1.0
- `alert_level`: SAFE, WARNING, or CRITICAL
- `features`: Dict of extracted features

**Example Usage:**
```python
from backend.services.ai_service import AIService

ai = AIService()
prediction = ai.predict(event, history=recent_events)

print(f"Prediction: {prediction.prediction_label.value}")
print(f"Confidence: {prediction.confidence:.1%}")
print(f"Alert: {prediction.alert_level.value}")
```

---

### 4. Alert Service

#### Class: `AlertService`

**Purpose:** Multi-channel alert notifications

**Methods:**

```python
AlertService(config: Optional[AlertConfig] = None)
```
- **Parameters:**
  - `config`: Alert configuration (optional)
- **Channels:** Console, Email, Telegram

```python
send_alert(event: MotionEvent, prediction: PredictionResult, force: bool = False) -> bool
```
- **Parameters:**
  - `event`: Motion event
  - `prediction`: AI prediction result
  - `force`: Send regardless of threshold
- **Returns:** True if sent successfully

```python
test_connection() -> Dict[str, bool]
```
- **Returns:** Dict of channel: status
- **Purpose:** Test all alert channels

**Example Usage:**
```python
from backend.services.alert_service import AlertService

alert = AlertService()

# Test channels
results = alert.test_connection()
# {'console': True, 'email': True, 'telegram': False}

# Send alert
success = alert.send_alert(event, prediction)
```

---

### 5. Database

#### Class: `Database`

**Purpose:** SQLite database operations

**Methods:**

```python
Database(db_path: str = "data/security.db")
```
- **Parameters:**
  - `db_path`: Path to SQLite database
- **Auto-creates:** Database and tables

```python
insert_event(event: MotionEvent, prediction: str = None, 
            alert_level: str = None, confidence: float = None) -> None
```
- **Parameters:**
  - `event`: MotionEvent object
  - `prediction`: AI prediction label (optional)
  - `alert_level`: Alert level (optional)
  - `confidence`: Confidence score (optional)

```python
get_recent_events(limit: int = 100) -> List[dict]
```
- **Parameters:**
  - `limit`: Max number of events
- **Returns:** List of event dictionaries (DESC order)

```python
get_statistics() -> Dict[str, int]
```
- **Returns:** Statistics dictionary
  - `total_events`: Total event count
  - `motion_detected`: Motion count
  - `today_events`: Events today
  - `suspicious_count`: Suspicious events

**Example Usage:**
```python
from backend.infrastructure.database import Database

db = Database()

# Insert event
db.insert_event(event, prediction="normal", confidence=0.89)

# Query recent
events = db.get_recent_events(limit=10)

# Statistics
stats = db.get_statistics()
print(f"Total: {stats['total_events']}")

db.close()
```

---

## Data Models

### MotionEvent

```python
@dataclass
class MotionEvent:
    timestamp: datetime
    motion: MotionStatus
    sensor_id: str = "PIR_001"
    location: str = "living_room"
```

**Fields:**
- `timestamp`: Event datetime
- `motion`: MOTION_DETECTED (1) or NO_MOTION (0)
- `sensor_id`: Unique sensor identifier
- `location`: Physical location

**Methods:**
- `to_dict() -> dict`: Convert to JSON-serializable dict
- `from_dict(data: dict) -> MotionEvent`: Create from dict

---

### PredictionResult

```python
@dataclass
class PredictionResult:
    timestamp: datetime
    motion_event: MotionEvent
    prediction_label: PredictionLabel
    confidence: float
    alert_level: AlertLevel
    features: dict
```

**Fields:**
- `timestamp`: Prediction time
- `motion_event`: Associated event
- `prediction_label`: NORMAL or SUSPICIOUS
- `confidence`: 0.0 - 1.0
- `alert_level`: SAFE, WARNING, CRITICAL
- `features`: Feature vector used

---

## Configuration

### MQTTConfig

```python
@dataclass
class MQTTConfig:
    broker: str
    port: int
    topic: str
    qos: int = 1
    client_id: str = "iot_security_client"
```

### AlertConfig

```python
@dataclass
class AlertConfig:
    email_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_ids: list = []
```

---

## REST API (Future Enhancement)

### Proposed Endpoints

```
GET  /api/events              # Get recent events
GET  /api/events/{id}         # Get specific event
GET  /api/statistics          # Get statistics
POST /api/predict             # Manual prediction
GET  /api/health              # System health
```

---

## MQTT Message Format

### Published by ESP32

```json
{
  "timestamp": "2026-01-06T14:30:00",
  "motion": 1,
  "sensor_id": "ESP32_PIR_nhom03",
  "location": "living_room"
}
```

**Topic:** `iot/security/pir/nhom03`  
**QoS:** 1

---

## Database Schema

### Table: `events`

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    motion INTEGER NOT NULL,
    sensor_id TEXT,
    location TEXT,
    prediction TEXT,
    confidence REAL,
    alert_level TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- Primary key on `id`
- Index on `timestamp` for faster queries

---

## Error Handling

### Common Exceptions

```python
# MQTT Connection Error
try:
    mqtt.connect()
except ConnectionError as e:
    print(f"Failed to connect: {e}")

# Model Loading Error
try:
    ai = AIService()
except FileNotFoundError:
    print("Model file not found")

# Database Error
try:
    db.insert_event(event)
except sqlite3.Error as e:
    print(f"Database error: {e}")
```

---

## Performance Guidelines

### Best Practices

1. **Database Queries:**
   - Use `limit` parameter to avoid large result sets
   - Query time should be < 100ms

2. **AI Predictions:**
   - Inference time < 100ms
   - Batch predictions when possible

3. **MQTT:**
   - Keep payload < 1KB
   - QoS 1 for guaranteed delivery
   - Reconnect on disconnect

4. **Memory:**
   - Close database connections
   - Limit history buffer size
   - Clean old events periodically

---

**Last Updated:** January 6, 2026  
**Version:** 1.0  
**Maintainer:** IoT Project Team
