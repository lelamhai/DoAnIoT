# 🏗️ KIẾN TRÚC HỆ THỐNG IoT SECURITY MONITORING

## 📊 SƠ ĐỒ TỔNG THỂ (ASCII Architecture)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     IoT SECURITY MONITORING SYSTEM                       │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  LAYER 1: SENSOR │
└──────────────────┘
         │
    ┌────▼────┐
    │ PIR HC- │      (Phát hiện chuyển động)
    │  SR501  │      Output: Digital 0/1
    └────┬────┘
         │
    ┌────▼────────┐
    │ ESP32/      │  - Đọc PIR signal
    │ Arduino     │  - WiFi connection (ESP32)
    └────┬────────┘  - Serial output (Arduino)
         │
         │ [Option A: WiFi]      [Option B: Serial]
         │                              │
         ▼                              ▼
┌────────────────────────────────────────────────────────────────┐
│  LAYER 2: NETWORK (MQTT)                                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│    ┌──────────────┐           ┌──────────────┐                │
│    │   Publisher  │───────────│ MQTT Broker  │                │
│    │ (ESP32/Py)   │           │ (Mosquitto)  │                │
│    └──────────────┘           └───────┬──────┘                │
│                                       │                        │
│                              Topic: iot/security/pir           │
│                              Payload: {"motion":1, "ts":"..."} │
└───────────────────────────────────────┬────────────────────────┘
                                        │
                                        ▼
┌────────────────────────────────────────────────────────────────┐
│  LAYER 3: APPLICATION (Backend)                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  MQTT Subscriber (Python)                               │  │
│  └───┬─────────────────────────────────────────────────────┘  │
│      │                                                         │
│      ├──────┐                                                  │
│      │      ▼                                                  │
│      │  ┌────────────────┐    ┌─────────────────┐             │
│      │  │ Data Processor │───▶│  Feature Eng.   │             │
│      │  │ - Validation   │    │  - hour_of_day  │             │
│      │  │ - Transform    │    │  - frequency    │             │
│      │  └────────────────┘    │  - duration     │             │
│      │                        └────────┬────────┘             │
│      │                                 │                      │
│      │                                 ▼                      │
│      │                        ┌─────────────────┐             │
│      │                        │  AI Classifier  │             │
│      │                        │ (Decision Tree) │             │
│      │                        │ Normal/Abnormal │             │
│      │                        └────────┬────────┘             │
│      │                                 │                      │
│      └─────────┬───────────────────────┘                      │
│                │                                               │
│                ▼                                               │
│   ┌────────────────────────┐                                  │
│   │  Storage Service       │                                  │
│   │  - SQLite DB           │                                  │
│   │  - CSV Logging         │                                  │
│   └────────────────────────┘                                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌────────────────────────────────────────────────────────────────┐
│  LAYER 4: PRESENTATION (Dashboard)                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Streamlit Dashboard (Web UI)                            │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │                                                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │ │
│  │  │  Real-time  │  │   Alert     │  │  Statistics    │  │ │
│  │  │   Status    │  │  Indicator  │  │   & Charts     │  │ │
│  │  │  🟢 / 🔴    │  │  🚨 / ✅     │  │  📊 📈 📉      │  │ │
│  │  └─────────────┘  └─────────────┘  └────────────────┘  │ │
│  │                                                          │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │  Event Log Table                                 │   │ │
│  │  │  Timestamp | Motion | AI Prediction | Status     │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘

         ┌──────────────────────────────────────┐
         │  NOTIFICATIONS (Optional)            │
         │  - Email alerts                      │
         │  - Telegram bot                      │
         │  - Sound alarm                       │
         └──────────────────────────────────────┘
```

---

## 📁 CẤU TRÚC FOLDER CHI TIẾT

```
DoAnIoT/
│
├── README.md                           # Tài liệu đề bài
├── system.md                           # Tài liệu kiến trúc (file này)
├── .gitignore
├── requirements.txt                    # Python dependencies
│
├── hardware/                           # Layer 1: Hardware code
│   ├── esp32/
│   │   └── pir_mqtt_publisher.ino     # ESP32 + WiFi + MQTT
│   ├── arduino/
│   │   └── pir_serial.ino             # Arduino serial output
│   └── schemas/
│       └── wiring_diagram.txt         # Sơ đồ đấu nối
│
├── backend/                            # Layer 3: Application logic
│   ├── __init__.py
│   ├── main.py                         # Entry point
│   │
│   ├── core/                           # Domain layer (business logic)
│   │   ├── __init__.py
│   │   ├── models.py                   # Data models (Motion, Event)
│   │   └── enums.py                    # MotionStatus, AlertLevel
│   │
│   ├── services/                       # Application layer
│   │   ├── __init__.py
│   │   ├── mqtt_service.py             # MQTT pub/sub logic
│   │   ├── data_processor.py           # Data validation & transform
│   │   ├── feature_engineering.py      # Extract AI features
│   │   ├── ai_service.py               # AI prediction
│   │   └── alert_service.py            # Alert notifications
│   │
│   ├── infrastructure/                 # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── database.py                 # SQLite connection
│   │   ├── logger.py                   # CSV/file logging
│   │   └── config.py                   # Configuration management
│   │
│   └── utils/
│       ├── __init__.py
│       └── helpers.py                  # Common utilities
│
├── ai_model/                           # AI/ML components
│   ├── __init__.py
│   ├── train.py                        # Model training script
│   ├── evaluate.py                     # Model evaluation
│   ├── data_generator.py               # Synthetic dataset generator
│   ├── models/
│   │   └── classifier.pkl              # Trained model
│   └── datasets/
│       ├── training_data.csv
│       └── test_data.csv
│
├── frontend/                           # Layer 4: Dashboard
│   ├── app.py                          # Streamlit main app
│   ├── components/
│   │   ├── __init__.py
│   │   ├── status_widget.py            # Real-time status display
│   │   ├── alert_widget.py             # Alert indicator
│   │   ├── chart_widget.py             # Statistics charts
│   │   └── log_table.py                # Event log table
│   ├── static/
│   │   ├── css/
│   │   │   └── custom.css
│   │   └── images/
│   │       ├── logo.png
│   │       └── alert.png
│   └── config.py                       # Frontend configuration
│
├── config/                             # Configuration files
│   ├── mqtt_config.yaml                # MQTT broker settings
│   ├── database_config.yaml            # Database settings
│   └── app_config.yaml                 # General app settings
│
├── logs/                               # Log storage
│   ├── events.csv                      # Event logs
│   ├── errors.log                      # Error logs
│   └── app.log                         # Application logs
│
├── data/                               # Data storage
│   └── security.db                     # SQLite database
│
├── tests/                              # Unit tests
│   ├── __init__.py
│   ├── test_mqtt_service.py
│   ├── test_data_processor.py
│   └── test_ai_service.py
│
├── scripts/                            # Utility scripts
│   ├── setup_database.py               # Initialize database
│   ├── mqtt_test_publisher.py          # Test MQTT manually
│   └── generate_mock_data.py           # Generate test data
│
└── docs/                               # Documentation
    ├── architecture.md                 # Architecture documentation
    ├── api.md                          # API documentation
    └── deployment.md                   # Deployment guide
```

---

## 🏛️ CLEAN ARCHITECTURE

### **Nguyên tắc thiết kế:**

```
┌──────────────────────────────────────────┐
│         Presentation Layer               │  ← Streamlit UI
│         (frontend/app.py)                │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│      Application Layer (Services)        │  ← Business logic
│  - mqtt_service.py                       │
│  - data_processor.py                     │
│  - ai_service.py                         │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│         Domain Layer (Core)              │  ← Models & Rules
│  - models.py (Motion, Event)             │
│  - enums.py (MotionStatus)               │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│    Infrastructure Layer                  │  ← External services
│  - database.py (SQLite)                  │
│  - logger.py (CSV)                       │
│  - config.py (YAML)                      │
└──────────────────────────────────────────┘
```

### **Dependency Rule:**
- ✅ Core không phụ thuộc vào Services/Infrastructure
- ✅ Services phụ thuộc vào Core
- ✅ Infrastructure phụ thuộc vào Core
- ✅ Presentation phụ thuộc vào Services

### **Lợi ích:**
- **Testability**: Dễ dàng unit test từng layer
- **Maintainability**: Thay đổi infrastructure không ảnh hưởng business logic
- **Scalability**: Dễ mở rộng thêm features
- **Separation of Concerns**: Mỗi layer có trách nhiệm rõ ràng

---

## 💻 CODE EXAMPLES

### **1. Domain Layer (Core)**

```python
# backend/core/models.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class MotionStatus(Enum):
    NO_MOTION = 0
    MOTION_DETECTED = 1

class AlertLevel(Enum):
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class MotionEvent:
    timestamp: datetime
    motion: MotionStatus
    sensor_id: str = "PIR_001"
    location: str = "living_room"
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "motion": self.motion.value,
            "sensor_id": self.sensor_id,
            "location": self.location
        }
    
@dataclass
class PredictionResult:
    is_abnormal: bool
    confidence: float
    alert_level: AlertLevel
    features: dict
```

### **2. Application Layer (Services)**

```python
# backend/services/mqtt_service.py
import paho.mqtt.client as mqtt
from backend.core.models import MotionEvent
from backend.infrastructure.config import MQTTConfig
import json
from typing import Callable

class MQTTService:
    def __init__(self, config: MQTTConfig):
        self.client = mqtt.Client()
        self.config = config
        self.message_callbacks = []
    
    def connect(self):
        self.client.connect(self.config.broker, self.config.port)
        self.client.loop_start()
    
    def subscribe(self, topic: str, callback: Callable):
        self.message_callbacks.append(callback)
        self.client.subscribe(topic)
        self.client.on_message = self._on_message
    
    def _on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        for callback in self.message_callbacks:
            callback(payload)
    
    def publish(self, topic: str, event: MotionEvent):
        payload = json.dumps(event.to_dict())
        self.client.publish(topic, payload)
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
```

```python
# backend/services/data_processor.py
from backend.core.models import MotionEvent, MotionStatus
from datetime import datetime
from typing import Dict, Optional

class DataProcessor:
    @staticmethod
    def validate_payload(payload: Dict) -> bool:
        required_fields = ["timestamp", "motion"]
        return all(field in payload for field in required_fields)
    
    @staticmethod
    def transform_to_event(payload: Dict) -> Optional[MotionEvent]:
        if not DataProcessor.validate_payload(payload):
            return None
        
        try:
            return MotionEvent(
                timestamp=datetime.fromisoformat(payload["timestamp"]),
                motion=MotionStatus(payload["motion"]),
                sensor_id=payload.get("sensor_id", "PIR_001"),
                location=payload.get("location", "living_room")
            )
        except Exception as e:
            print(f"Transform error: {e}")
            return None
```

### **3. Infrastructure Layer**

```python
# backend/infrastructure/database.py
import sqlite3
from typing import List, Optional
from backend.core.models import MotionEvent
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "data/security.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                motion INTEGER NOT NULL,
                sensor_id TEXT,
                location TEXT,
                prediction TEXT,
                alert_level TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def insert_event(self, event: MotionEvent, 
                     prediction: Optional[str] = None,
                     alert_level: Optional[str] = None):
        self.conn.execute('''
            INSERT INTO events (timestamp, motion, sensor_id, location, prediction, alert_level)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp.isoformat(),
            event.motion.value,
            event.sensor_id,
            event.location,
            prediction,
            alert_level
        ))
        self.conn.commit()
    
    def get_recent_events(self, limit: int = 100) -> List[dict]:
        cursor = self.conn.execute('''
            SELECT * FROM events 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        if self.conn:
            self.conn.close()
```

```python
# backend/infrastructure/config.py
import yaml
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MQTTConfig:
    broker: str
    port: int
    topic: str
    username: str = None
    password: str = None

@dataclass
class DatabaseConfig:
    path: str
    backup_enabled: bool = True

class ConfigManager:
    @staticmethod
    def load_mqtt_config(path: str = "config/mqtt_config.yaml") -> MQTTConfig:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return MQTTConfig(**data['mqtt'])
    
    @staticmethod
    def load_database_config(path: str = "config/database_config.yaml") -> DatabaseConfig:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return DatabaseConfig(**data['database'])
```

---

## 📋 ROADMAP CHI TIẾT

### **Phase 1: Project Setup (0.5 ngày)**
- ✅ Tạo folder structure
- ✅ Setup .gitignore, requirements.txt
- ✅ Tạo core models (MotionEvent, enums)
- ✅ Setup configuration files (YAML)
- ✅ Initialize SQLite database

**Deliverables:**
- Folder structure hoàn chỉnh
- Core models và enums
- Config files template

---

### **Phase 2: MQTT Infrastructure (1 ngày)**
- ✅ Implement MQTT service (paho-mqtt)
- ✅ Tạo MQTT test publisher/subscriber
- ✅ Test connection với broker public
- ✅ Implement data processor
- ✅ Validate JSON payload

**Deliverables:**
- `backend/services/mqtt_service.py`
- `backend/services/data_processor.py`
- `scripts/mqtt_test_publisher.py`
- Test successful MQTT communication

---

### **Phase 3: Hardware Integration (1 ngày)**

#### **Option A: ESP32 (Recommended)**
```cpp
// hardware/esp32/pir_mqtt_publisher.ino
#include <WiFi.h>
#include <PubSubClient.h>

#define PIR_PIN 27
const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
const char* mqtt_server = "broker.hivemq.com";
const char* topic = "iot/security/pir";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  pinMode(PIR_PIN, INPUT);
  WiFi.begin(ssid, password);
  client.setServer(mqtt_server, 1883);
}

void loop() {
  int motion = digitalRead(PIR_PIN);
  String payload = "{\"timestamp\":\"" + getTimestamp() + 
                   "\",\"motion\":" + String(motion) + "}";
  client.publish(topic, payload.c_str());
  delay(200);
}
```

#### **Option B: Arduino + Serial Bridge**
```python
# backend/services/serial_bridge.py
import serial
import json
from backend.services.mqtt_service import MQTTService

class SerialBridge:
    def __init__(self, port: str, mqtt_service: MQTTService):
        self.serial = serial.Serial(port, 115200)
        self.mqtt_service = mqtt_service
    
    def read_and_publish(self):
        while True:
            if self.serial.in_waiting:
                data = self.serial.readline().decode().strip()
                motion = int(data)
                payload = {
                    "timestamp": datetime.now().isoformat(),
                    "motion": motion
                }
                self.mqtt_service.publish("iot/security/pir", payload)
```

**Deliverables:**
- ESP32/Arduino code
- Serial bridge (if using Arduino)
- Hardware wiring diagram

---

### **Phase 4: Backend + Logging (1 ngày)**
- ✅ CSV logging service
- ✅ Database integration
- ✅ Backend main entry point
- ✅ End-to-end test: PIR → MQTT → Backend → Database

**Deliverables:**
- `backend/infrastructure/logger.py`
- `backend/main.py`
- Working pipeline: Sensor → Database

---

### **Phase 5: AI/ML Implementation (2 ngày)**

#### **Day 1: Dataset & Features**
```python
# ai_model/data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_training_data(n_samples=500):
    data = []
    start = datetime(2026, 1, 1, 0, 0, 0)
    
    for i in range(n_samples):
        timestamp = start + timedelta(minutes=i*5)
        hour = timestamp.hour
        
        # Normal patterns (8h-22h)
        if 8 <= hour <= 22:
            motion = np.random.choice([0, 1], p=[0.3, 0.7])
            label = 0  # Normal
        # Suspicious patterns (22h-8h)
        else:
            motion = np.random.choice([0, 1], p=[0.8, 0.2])
            label = 1 if motion == 1 else 0  # Suspicious if motion
        
        data.append({
            "timestamp": timestamp.isoformat(),
            "motion": motion,
            "hour": hour,
            "label": label
        })
    
    return pd.DataFrame(data)
```

```python
# backend/services/feature_engineering.py
import pandas as pd

class FeatureEngineer:
    @staticmethod
    def extract_features(events: pd.DataFrame) -> pd.DataFrame:
        df = events.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 6)).astype(int)
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Motion features (rolling window)
        df['motion_freq_10min'] = df['motion'].rolling(window=10, min_periods=1).sum()
        df['motion_freq_30min'] = df['motion'].rolling(window=30, min_periods=1).sum()
        
        # Duration features
        df['motion_duration'] = df.groupby((df['motion'] != df['motion'].shift()).cumsum())['motion'].transform('size')
        
        return df
```

#### **Day 2: Training & Evaluation**
```python
# ai_model/train.py
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def train_model():
    # Load data
    df = pd.read_csv('ai_model/datasets/training_data.csv')
    
    # Features
    X = df[['hour', 'is_night', 'motion_freq_10min', 'motion_duration']]
    y = df['label']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Train
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # Save
    joblib.dump(model, 'ai_model/models/classifier.pkl')
    
    return model
```

**Deliverables:**
- Synthetic dataset (500 records)
- Feature engineering pipeline
- Trained model (classifier.pkl)
- Evaluation report (75-85% accuracy)

---

### **Phase 6: Dashboard (2 ngày)**

```python
# frontend/app.py
import streamlit as st
from backend.infrastructure.database import Database
import plotly.express as px

st.set_page_config(page_title="IoT Security Monitor", layout="wide")

# Header
st.title("🔒 IoT Security Monitoring System")

# Real-time status
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Status", "🟢 SAFE" if latest_safe else "🔴 ALERT")
with col2:
    st.metric("Today's Events", total_events)
with col3:
    st.metric("Suspicious Activity", suspicious_count)

# Charts
st.subheader("📊 Activity Timeline")
fig = px.line(df, x='timestamp', y='motion', title='Motion Detection Over Time')
st.plotly_chart(fig, use_container_width=True)

# Event log
st.subheader("📋 Recent Events")
st.dataframe(recent_events, use_container_width=True)
```

**Deliverables:**
- Streamlit dashboard
- Real-time status widget
- Alert indicator
- Charts (timeline, statistics)
- Event log table

---

### **Phase 7: Integration & Alerts (1 ngày)**
- ✅ Integrate all components
- ✅ Alert service (optional: email/telegram)
- ✅ End-to-end testing
- ✅ Performance optimization

**Deliverables:**
- Full working system
- Alert notifications
- Integration tests

---

### **Phase 8: Testing & Documentation (1.5 ngày)**
- ✅ Unit tests (pytest)
- ✅ Documentation (architecture, API, deployment)
- ✅ Demo scenarios preparation
- ✅ Final report

**Deliverables:**
- Test coverage report
- Complete documentation
- Demo video/screenshots
- Final report PDF

---

## 📅 TIMELINE SUMMARY

| Phase | Duration | Dependencies | Status |
|-------|----------|--------------|--------|
| Phase 1: Setup | 0.5 day | - | ⏳ Pending |
| Phase 2: MQTT | 1 day | Phase 1 | ⏳ Pending |
| Phase 3: Hardware | 1 day | Phase 2 | ⏳ Pending |
| Phase 4: Backend | 1 day | Phase 2, 3 | ⏳ Pending |
| Phase 5: AI/ML | 2 days | Phase 4 | ⏳ Pending |
| Phase 6: Dashboard | 2 days | Phase 4 | ⏳ Pending |
| Phase 7: Integration | 1 day | Phase 5, 6 | ⏳ Pending |
| Phase 8: Testing | 1.5 days | All | ⏳ Pending |
| **TOTAL** | **10 days** | | |

---

## 🔧 TECH STACK

### **Hardware**
- PIR HC-SR501 (Motion Sensor)
- ESP32 / Arduino Uno
- Breadboard & Jumper Wires

### **Backend**
- Python 3.8+
- paho-mqtt (MQTT client)
- SQLite (Database)
- pandas (Data processing)
- scikit-learn (AI/ML)
- PyYAML (Configuration)

### **Frontend**
- Streamlit (Dashboard)
- Plotly (Charts)
- Bootstrap (Optional styling)

### **Infrastructure**
- MQTT Broker: Mosquitto / HiveMQ Cloud
- Version Control: Git
- Testing: pytest

---

## 📊 DATA FLOW

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   PIR   │────▶│  ESP32   │────▶│   MQTT   │────▶│ Backend  │
│ Sensor  │     │  /WiFi   │     │  Broker  │     │ Subscriber│
└─────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                     ┌──────────────────────────────────┘
                     │
      ┌──────────────┴──────────────┐
      │                             │
      ▼                             ▼
┌────────────┐              ┌──────────────┐
│  Database  │              │ Feature Eng. │
│  (SQLite)  │              │  + AI Model  │
└────────────┘              └──────┬───────┘
      │                            │
      │                            ▼
      │                    ┌───────────────┐
      │                    │  Prediction   │
      │                    │ Normal/Abnormal│
      │                    └───────┬───────┘
      │                            │
      └────────────┬───────────────┘
                   │
                   ▼
            ┌─────────────┐
            │  Dashboard  │
            │ (Streamlit) │
            └─────────────┘
```

---

## ✅ ACCEPTANCE CRITERIA

### **Yêu cầu bắt buộc:**
- [x] PIR sensor phát hiện chuyển động (0/1)
- [x] MQTT publish/subscribe hoạt động
- [x] Dashboard hiển thị trạng thái real-time
- [x] Hệ thống cảnh báo khi phát hiện chuyển động
- [x] Logging dữ liệu (CSV + Database)
- [x] Báo cáo kiến trúc và demo

### **Yêu cầu tùy chọn:**
- [x] AI classification (Normal/Abnormal)
- [ ] Email/Telegram notifications
- [ ] Multi-sensor support
- [ ] Cloud deployment

---

## 🚀 GETTING STARTED

### **Quick Start:**
```bash
# 1. Clone repository
git clone <repo_url>
cd DoAnIoT

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup database
python scripts/setup_database.py

# 4. Run backend
python backend/main.py

# 5. Run dashboard (new terminal)
streamlit run frontend/app.py

# 6. Upload Arduino/ESP32 code
# Open Arduino IDE → hardware/esp32/pir_mqtt_publisher.ino
```

---

## 📞 SUPPORT & ISSUES

Nếu gặp vấn đề trong quá trình triển khai, tham khảo:
- `docs/architecture.md` - Chi tiết kiến trúc
- `docs/api.md` - API documentation
- `docs/deployment.md` - Deployment guide

---

**Generated:** January 6, 2026  
**Version:** 1.0  
**Author:** IoT Project Team
