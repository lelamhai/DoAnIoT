# Face Recognition Camera App (Python) — Vibe Coding Pack (MVP + SQLite)

Mục tiêu: App Python nhận diện **Người thân / Người lạ** từ camera realtime và **lưu SQLite chỉ gồm `name` + `time`**.  
Không lưu ảnh, không log chi tiết (score/frame/box...), chỉ lưu đúng yêu cầu tối giản.

> MVP đề xuất: **OpenCV + face_recognition (dlib) + SQLite**  
> Nâng cấp sau: InsightFace, Web UI/API, anti-spoofing.

---

## 1) Kiến trúc tổng thể (ASCII)

### 1.1 Luồng realtime nhận diện (Updated với Stranger Alert)

```
+------------------+     +---------------------+     +----------------------+
|   Camera (CV2)   | --> |  Preprocess Frame   | --> | Detect + Encode Face |
| VideoCapture()   |     | resize, BGR->RGB    |     | (Face Engine Port)   |
+------------------+     +---------------------+     +----------+-----------+
                                                                 |
                                                                 v
                                                      +---------------------+
                                                      |  Match Known/Unknown|
                                                      |  (Match Policy)     |
                                                      +----------+----------+
                                                                 |
                              +----------------------------------+------------------+
                              |                                                     |
                              v                                                     v
                    +-------------------+                                 +----------------------+
                    |  UI Presenter     |                                 | SQLite Repository    |
                    | draw bbox + label |                                 | insert(name, time)   |
                    +-------------------+                                 +----------+-----------+
                                                                                     |
                                                                                     v
                                                                          +----------------------+
                                                                          | Stranger Monitor     |
                                                                          | Track stranger count |
                                                                          +----------+-----------+
                                                                                     |
                                                                    (threshold exceeded ≥10/60s)
                                                                                     |
                                                                                     v
                                                                          +----------------------+
                                                                          | Email Service (SMTP) |
                                                                          | Send alert to family |
                                                                          +----------------------+
```

### 1.2 Clean Architecture (layered)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Presentation (UI)                                                          │
│ - OpenCV Window (MVP) / Streamlit / FastAPI                                 │
└───────────────▲────────────────────────────────────────────────────────────┘
                │ calls use cases
┌───────────────┴────────────────────────────────────────────────────────────┐
│ Application (Use Cases)                                                    │
│ - RecognizeFrameUseCase: orchestrate detect->encode->match->persist         │
│ - LoadKnownFacesUseCase: load dataset ảnh người thân                        │
└───────────────▲────────────────────────────────────────────────────────────┘
                │ depends on interfaces (ports)
┌───────────────┴────────────────────────────────────────────────────────────┐
│ Domain (Entities + Policies + Ports)                                       │
│ - Entities: BoundingBox, RecognitionEvent                                  │
│ - Policy: MatchPolicy(tolerance)                                            │
│ - Ports: FaceEnginePort, KnownFaceRepoPort, RecognitionRepoPort             │
└───────────────▲────────────────────────────────────────────────────────────┘
                │ implemented by adapters
┌───────────────┴────────────────────────────────────────────────────────────┐
│ Infrastructure (Adapters)                                                   │
│ - face_recognition engine adapter                                            │
│ - filesystem dataset loader (known_faces/<name>/*.jpg)                      │
│ - OpenCV camera adapter                                                      │
│ - SQLite repository (chỉ name + time)                                       │
│ - Stranger Monitor (sliding window tracking)                                 │
│ - Email Notification Service (SMTP for alerts)                               │
└────────────────────────────────────────────────────────────────────────────┘
```

**Nguyên tắc:**  
- UI không gọi trực tiếp logic face_recognition.  
- Use case chỉ gọi qua **Port**.  
- Thay engine/DB không ảnh hưởng các layer trên.

---

## 2) Cấu trúc folder (đề xuất cho MVP)

```
face-app/
├─ README.md
├─ requirements.txt
├─ known_faces/                     # bạn cung cấp ảnh + tên người thân
│  ├─ Linh/
│  │  ├─ 01.jpg
│  │  └─ 02.jpg
│  └─ Nam/
│     └─ 01.jpg
├─ data/
│  └─ attendance.sqlite             # auto-create khi chạy
├─ docs/
│  ├─ EMAIL_SETUP.md                # hướng dẫn setup Gmail App Password
│  └─ PHASE4_GUIDE.md               # advanced features guide
├─ esp32_pir_mqtt/                   # ESP32 Arduino firmware
│  ├─ esp32_pir_mqtt.ino            # main Arduino code
│  └─ README.md                     # hardware setup guide
└─ src/
   └─ face_app/
      ├─ __init__.py
      ├─ main.py                    # entrypoint chạy OpenCV app
      ├─ config/
      │  └─ settings.py             # CAM_INDEX, TOLERANCE, EMAIL_CONFIG
      ├─ domain/
      │  ├─ entities.py             # BoundingBox, RecognitionEvent...
      │  ├─ ports.py                # Interfaces
      │  └─ policies.py             # MatchPolicy
      ├─ application/
      │  ├─ dto.py                  # ViewModel cho UI
      │  └─ usecases/
      │     ├─ load_known_faces.py
      │     └─ recognize_frame.py   # + stranger monitoring
      ├─ infrastructure/
      │  ├─ camera/
      │  │  └─ opencv_camera.py
      │  ├─ face_engines/
      │  │  └─ fr_dlib_engine.py
      │  ├─ repos/
      │  │  ├─ filesystem_known_repo.py
      │  │  └─ sqlite_recognition_repo.py
      │  ├─ monitoring/
      │  │  ├─ stranger_monitor.py        # track strangers, trigger alerts
      │  │  └─ person_detection_monitor.py # track known persons
      │  ├─ notifications/
      │  │  └─ email_service.py            # SMTP email sender
      │  └─ iot/
      │     └─ mqtt_client.py              # MQTT client for PIR sensor
      └─ presentation/
         └─ opencv_app.py            # loop: capture -> usecase -> draw -> show
```
      │     └─ recognize_frame.py
      ├─ infrastructure/
      │  ├─ camera/
      │  │  └─ opencv_camera.py
      │  ├─ face_engines/
      │  │  └─ fr_dlib_engine.py
      │  └─ repos/
      │     ├─ filesystem_known_repo.py
      │     └─ sqlite_recognition_repo.py
      └─ presentation/
         └─ opencv_app.py            # loop: capture -> usecase -> draw -> show
```

---

## 3) Cấu trúc code (Clean Architecture dễ maintain)

### 3.1 Domain (Ports / Policy / Entities)

**Entities (`domain/entities.py`)**
- `BoundingBox(top, right, bottom, left)`
- `RecognitionEvent(name: str, time: str)` (MVP chỉ lưu 2 field)
- `FaceMatch(name: str, is_known: bool, distance: float)` (phục vụ UI)

**Ports (`domain/ports.py`)**
- `FaceEnginePort`
  - `detect(rgb_frame) -> list[BoundingBox]`
  - `encode(rgb_frame, boxes) -> list[vector]`
  - `distance(known_vectors, probe_vector) -> list[float]`
- `KnownFaceRepoPort`
  - `list_known() -> list[(name, vector)]`
- `RecognitionRepoPort`
  - `insert(name: str, time: str) -> None`

**Policy (`domain/policies.py`)**
- `MatchPolicy(tolerance: float)`:
  - input: known vectors + probe vector
  - output: `FaceMatch`
  - rule: `min_distance < tolerance => known else Stranger`

> **Chống spam DB:** thêm rule cooldown ở Application (ví dụ 10 giây) để không insert liên tục mỗi frame.

---

### 3.2 Application (Use Cases)

**Use case: LoadKnownFaces**
- Đọc `known_faces/<name>/*.jpg`
- Dùng `FaceEngine` tạo encoding
- Trả ra `known_encodings + known_names` (hoặc map name -> vectors)

**Use case: RecognizeFrame**
- Input: `frame_bgr`
- Preprocess: resize + BGR->RGB
- Detect + Encode
- Match (MatchPolicy)
- **Persist SQLite**: `insert(name, time)` theo rule cooldown
- Return ViewModel cho UI: boxes + label

---

### 3.3 Infrastructure (Adapters)

- `OpenCVCamera` đọc frame BGR
- `FRDlibEngine` adapter gọi `face_recognition`:
  - `face_locations`, `face_encodings`, `face_distance`
- `FilesystemKnownRepo` load dataset từ folder `known_faces/`
- `SQLiteRecognitionRepo`:
  - tạo bảng nếu chưa có
  - insert đúng 2 cột `name`, `time`

---

### 3.4 Presentation (OpenCV UI)

- `opencv_app.py`:
  - loop: `camera.read()` -> `RecognizeFrameUseCase.execute(frame)` -> draw -> show
  - nhấn `q` để thoát

---

## 4) SQLite (đúng yêu cầu: chỉ lưu tên + thời gian)

**DB file:** `data/attendance.sqlite`

**Table:** `recognitions`

```sql
CREATE TABLE IF NOT EXISTS recognitions (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  time TEXT NOT NULL
);
```

**Ví dụ dữ liệu:**
- `Linh | 2026-01-09 22:30:10`
- `Stranger | 2026-01-09 22:30:18`

---

## 5) Quy tắc ghi SQLite (tránh spam)

Vì camera chạy theo frame, nếu insert mỗi frame sẽ “nổ DB”.  
MVP nên dùng 1 trong 2 rule:

1) **Cooldown theo thời gian** (khuyên dùng):
- Với mỗi `name`, chỉ ghi lại sau `COOLDOWN_SECONDS` (vd 10s)

2) **Chỉ ghi khi tên thay đổi**:
- Frame trước Linh → frame sau Linh: không ghi
- Linh → Stranger: ghi

Có thể kết hợp cả 2.

---

## 6) List task & Roadmap rõ ràng

### Phase 0 — Setup (0.5 ngày)
- [ ] Khởi tạo repo + structure
- [ ] `requirements.txt` (opencv-python, face_recognition, numpy)
- [ ] Tạo `known_faces/` theo chuẩn folder người thân
- [ ] Test camera OpenCV

**Deliverable:** mở được camera.

---

### Phase 1 — MVP Recognize + SQLite (1–2 ngày)
- [ ] Implement `FRDlibEngine` (FaceEnginePort)
- [ ] Implement `FilesystemKnownRepo` load ảnh người thân
- [ ] Implement `MatchPolicy(tolerance)`
- [ ] Implement `SQLiteRecognitionRepo` (name + time)
- [ ] Implement `RecognizeFrameUseCase` + cooldown
- [ ] Implement OpenCV UI (draw bbox + label)
- [ ] Smoke test: người thân → insert tên, người lạ → insert "Stranger"

**Deliverable:** chạy realtime + lưu SQLite đúng yêu cầu.

---

### Phase 2 — Nâng cấp nhẹ (2–4 ngày, optional)
- [ ] Cache encodings (load nhanh, tránh encode lại mỗi lần)
- [ ] Hot reload dataset (thêm ảnh không cần restart)
- [ ] Unit tests cho policy + repo
- [ ] Thêm config qua `.env`

---

### Phase 3 — UI/Service hóa (optional)
- [ ] Streamlit dashboard xem danh sách `recognitions`
- [ ] FastAPI endpoint `/recognize` & `/events` (lấy dữ liệu SQLite)

---

### Phase 4 — Accuracy/Performance (optional)
- [ ] InsightFace engine
- [ ] Tracking để giảm compute
- [ ] Multi-thread capture/recognize
- [ ] Liveness (nếu dùng security)

---

### Phase 5 — Security & Monitoring (COMPLETED ✅)
- [x] **Stranger Detection Monitor**: Theo dõi người lạ trong sliding window
  - Sliding window: 60 giây
  - Threshold: 10 detections
  - Auto-reset nếu < threshold
  
- [x] **Known Person Detection Monitor**: Theo dõi người thân
  - Sliding window: 60 giây  
  - Threshold: 10 detections (giống người lạ)
  - Không gửi email, chỉ ghi database
  
- [x] **Email Alert System**: Gửi cảnh báo qua Gmail SMTP
  - Integration với Gmail App Password
  - Email template tiếng Việt
  - Alert cooldown: 5 phút (tránh spam)
  - Test email function
  
- [x] **UI Integration**: Hiển thị stranger counter trên video
  - Real-time counter display
  - Color coding (red warning when near threshold)

**Implementation Details:**
```python
# Detection Monitor workflow:
1. Record every detection (stranger or known)
2. Cleanup old detections (> 60s)
3. Count detections in window
4. Stranger: If ≥10 → Email + DB
5. Known Person: If ≥10 → DB only (no email)
6. Auto-reset after threshold
```

**Email Configuration:**
```python
# settings.py
ENABLE_STRANGER_ALERTS = True
STRANGER_TIME_WINDOW = 60  # seconds
STRANGER_THRESHOLD = 10
STRANGER_ALERT_COOLDOWN = 300  # seconds

ENABLE_KNOWN_PERSON_TRACKING = True
KNOWN_PERSON_TIME_WINDOW = 60  # seconds
KNOWN_PERSON_THRESHOLD = 10  # SAME as stranger
KNOWN_PERSON_LOG_COOLDOWN = 0

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your@gmail.com"
SENDER_PASSWORD = "app_password"  # Gmail App Password (NOT regular password!)
RECIPIENT_EMAILS = ["family@gmail.com"]
```

**Setup Gmail App Password:**
1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use 16-character password (not regular password)

**Testing:**
```bash
# Test email configuration
python test_email.py

# Run with alerts
python run_advanced.py
```

**Deliverable:** 
- Tự động gửi email cảnh báo khi phát hiện người lạ ≥10 lần/60s
- Ghi database khi người thân xuất hiện ≥10 lần/60s
- Real-time monitoring trên UI
- Configurable thresholds và cooldowns

---

### Phase 6 — IoT Integration với ESP32 + PIR (COMPLETED ✅)

- [x] **MQTT Communication**: Kết nối với ESP32 qua MQTT
  - Broker: broker.hivemq.com (public)
  - Topic: `iot/nhom03/security/pir`
  - Protocol: MQTT 1883
  - Client ID: face_recognition_app_nhom03
  
- [x] **Active Control Variable**: Biến điều khiển ghi DB và email
  - `active = True`: Cho phép ghi database + gửi email
  - `active = False`: Chỉ nhận diện và hiển thị, không ghi/gửi
  - Điều khiển bằng PIR sensor hoặc phím 'A' thủ công
  
- [x] **PIR Sensor Integration**: ESP32 với cảm biến PIR HC-SR501
  - PIR phát hiện chuyển động → Gửi "1" → active = True
  - PIR không phát hiện → Gửi "0" → active = False
  - Debounce: 500ms
  - Heartbeat: Gửi message mỗi 1 giây
  
- [x] **ESP32 Arduino Code**: Firmware hoàn chỉnh
  - WiFi connection với auto-retry
  - MQTT client với auto-reconnect
  - PIR reading với debounce logic
  - LED indicator (GPIO 2)
  - Serial logging chi tiết
  - 30 giây PIR warm-up time

**Architecture:**
```
┌─────────────┐   WiFi    ┌──────────────┐   MQTT    ┌─────────────────┐
│ PIR Sensor  │──────────▶│    ESP32     │──────────▶│ MQTT Broker     │
│  HC-SR501   │   GPIO13  │              │  Publish  │ (HiveMQ.com)    │
└─────────────┘           └──────────────┘           └────────┬────────┘
                                                               │ Subscribe
                                                               ▼
                                                    ┌─────────────────────┐
                                                    │  Python App         │
                                                    │  (Face Recognition) │
                                                    └─────────────────────┘
```

**MQTT Message Flow:**
```python
# ESP32 → MQTT Broker → Python App

PIR = HIGH (Motion detected)
  → ESP32 publish "1" to iot/nhom03/security/pir
  → Python receives "1"
  → active = True
  → Enable DB logging + Email alerts

PIR = LOW (No motion)
  → ESP32 publish "0" to iot/nhom03/security/pir
  → Python receives "0"
  → active = False
  → Disable DB/Email (display only)
```

**Python MQTT Configuration:**
```python
# settings.py
ENABLE_PIR_CONTROL = True
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "face_recognition_app_nhom03"
MQTT_TOPIC_PIR = "iot/nhom03/security/pir"
MQTT_KEEPALIVE = 60
```

**ESP32 Configuration:**
```cpp
// esp32_pir_mqtt.ino
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "broker.hivemq.com";
const char* mqtt_topic = "iot/nhom03/security/pir";
const int PIR_PIN = 13;  // GPIO 13
```

**Hardware Connection:**
```
PIR HC-SR501          ESP32
┌──────────┐        ┌─────────┐
│   VCC    │───────▶│   5V    │
│   OUT    │───────▶│ GPIO 13 │
│   GND    │───────▶│   GND   │
└──────────┘        └─────────┘
```

**Testing:**
```bash
# 1. Upload ESP32 code (Arduino IDE)
# 2. Monitor ESP32 Serial (115200 baud)
# 3. Run Python app
python run_advanced.py

# 4. Quan sát:
# - ESP32: Khi PIR trigger → "📤 Published: 1"
# - Python: "🟢 PIR: Motion detected → ACTIVE = True"
# - ESP32: Khi PIR idle → "📤 Published: 0"  
# - Python: "🔴 PIR: No motion → ACTIVE = False"
```

**UI Display:**
```
📡 MQTT PIR Control: Connected
📊 ACTIVE mode: True (BẬT = ghi DB/email, TẮT = chỉ hiển thị)

MQTT: Connected ✅
ACTIVE: ON (DB+Email) 🟢  ← Điều khiển bởi PIR
```

**Manual Override:**
- Phím **'A'**: Toggle active manually (khi không có PIR)
- Phím **'R'**: Reload known faces
- Phím **'Q'**: Quit application

**Logic Tổng Hợp:**
```python
# Khi active = True (PIR = 1 hoặc manual):
- Stranger ≥10 lần/60s → Ghi DB + Gửi Email ✅
- Known Person ≥10 lần/60s → Ghi DB ✅

# Khi active = False (PIR = 0):
- Stranger → Chỉ hiển thị, không ghi DB, không email ❌
- Known Person → Chỉ hiển thị, không ghi DB ❌
```

**Deliverable:**
- ✅ ESP32 firmware hoàn chỉnh với PIR + MQTT
- ✅ Python MQTT client non-blocking
- ✅ Active control variable điều khiển toàn bộ logging
- ✅ Real-time PIR status trên UI
- ✅ Manual override capability
- ✅ Comprehensive documentation (README.md)

---

## 7) Quickstart (MVP + Stranger Alerts)

1) Cài dependencies:
```bash
pip install -r requirements.txt
```

2) Thêm ảnh người thân:
```
known_faces/Linh/01.jpg
known_faces/Nam/01.jpg
```

3) Setup Email (Optional - cho stranger alerts):
```bash
# Xem hướng dẫn chi tiết: docs/EMAIL_SETUP.md

# Lấy Gmail App Password:
# 1. https://myaccount.google.com/security → Bật 2FA
# 2. https://myaccount.google.com/apppasswords → Tạo password
# 3. Update vào src/face_app/config/settings.py:
#    SENDER_EMAIL = "your@gmail.com"
#    SENDER_PASSWORD = "ctym wxnc eklc frzw"  # 16-char App Password
#    RECIPIENT_EMAILS = ["family@gmail.com"]

# Test email:
python test_email.py
```
, no IoT)
python run.py

# Advanced mode (với stranger alerts + MQTT PIR control)
python run_advanced.py
```

5) Kết quả:
- UI hiển thị `Linh` hoặc `Stranger`
- SQLite có record `name + time` (khi active=True)
- **Phase 5:** Email cảnh báo khi ≥10 người lạ trong 60s
- **Phase 5:** UI hiển thị "Strangers: X/10" counter real-time
- **Phase 6:** MQTT status: Connected/Disconnected
- **Phase 6:** ACTIVE status: ON/OFF (điều khiển bởi PIR hoặc phím 'A')
- **Phase 6:** PIR sensor tự động BẬT/TẮT chức năng logging
- SQLite có record `name + time`
- **NEW (Phase 5):** Email cảnh báo khi ≥10 người lạ trong 60s
- **NEW (Phase 5):** UI hiển thị "Strangers: X/10" counter real-time

---

## 8) Notes thực chiến
- Mỗi người nên có **3–10 ảnh** (nhiều góc + ánh sáng)
- `TOLERANCE` khuyến nghị start ở **0.5** (siết: 0.45, nới: 0.55)
- Windows đôi khi khó cài `dlib/face_recognition`; nếu gặp lỗi build thì chuyển sang:
  - Conda, h/Known threshold:** Cả 2 đều là 10 lần/60s
- **Alert cooldown:** Mặc định 5 phút giữa các email để tránh spam
- **MQTT Broker:** Dùng public broker broker.hivemq.com (hoặc tự host)
- **PIR Sensor:** HC-SR501, điều chỉnh sensitivity và time delay bằng trimpot
- **WiFi:** ESP32 chỉ hỗ trợ 2.4GHz, không hỗ trợ 5GHz
- **Active Control:** 
  - `active=True`: Ghi DB + Email (khi PIR phát hiện chuyển động)
  - `active=False`: Chỉ hiển thị (khi PIR không phát hiện)
  - Có thể toggle thủ công bằng phím 'A'
- **Email alerts:** Phải dùng Gmail App Password, không dùng mật khẩu thường
- **Stranger threshold:** Điều chỉnh `STRANGER_THRESHOLD` và `STRANGER_TIME_WINDOW` trong settings.py
- **Alert cooldown:** Mặc định 5 phút giữa các email để tránh spam

---

## 9) Architecture Patterns Used

**Clean Architecture Benefits:**/Known person detection tracking
- **Pub-Sub Pattern**: MQTT communication for IoT integration

**Key Components:**

```python
# Domain Layer (business rules)
- MatchPolicy: tolerance-based matching
- Entities: BoundingBox, FaceMatch, RecognitionEvent

# Application Layer (orchestration)
- RecognizeFrameUseCase: main recognition pipeline with active control
- LoadKnownFacesUseCase: dataset loading

# Infrastructure Layer (external services)
- FRDlibEngine / InsightFaceEngine: face recognition
- SQLiteRecognitionRepo: persistence
- StrangerMonitor: sliding window tracking (10/60s → email + DB)
- PersonDetectionMonitor: known person tracking (10/60s → DB only)
- EmailNotificationService: SMTP alerts
- MQTTClient: IoT communication with ESP32

# Presentation Layer (UI)
- OpenCVApp: real-time video UI with alerts + MQTT status
- Streamlit Dashboard: web analytics
- FastAPI: REST API
```

**IoT Components:**

```cpp
// ESP32 Firmware (Arduino)
- WiFi connection management
- MQTT client (PubSubClient)
- PIR sensor reading with debounce
- State publishing (0/1)
- Heartbeat mechanism
```

**Data Flow with IoT:**

```
┌─────────┐  GPIO  ┌─────────┐  MQTT   ┌──────────┐  Callback  ┌──────────────┐
│   PIR   │───────▶│  ESP32  │────────▶│  Broker  │───────────▶│  Python App  │
│ Sensor  │   13   │         │  Pub 1  │ HiveMQ   │  Sub topic │  (OpenCV UI) │
└─────────┘        └─────────┘         └──────────┘            └──────┬───────┘
                                                                       │
                                                                  Set active
                                                                       │
                                                                       ▼
                                                            ┌──────────────────┐
                                                            │ RecognizeFrame   │
                                                            │ if active:       │
                                                            │   - Log DB       │
                                                            │   - Send Email   │
                                                            └──────────────────┘
# Infrastructure Layer (external services)
- FRDlibEngine / InsightFaceEngine: face recognition
- SQLiteRecognitionRepo: persistence
- StrangerMonitor: sliding window tracking
- EmailNotificationService: SMTP alerts

# Presentation Layer (UI)
- OpenCVApp: real-time video UI with alerts
- Streamlit Dashboard: web analytics
- FastAPI: REST API
```

---

Nếu bạn muốn, mình có thể generate luôn **toàn bộ skeleton code MVP** đúng theo README này để bạn chạy ngay.
