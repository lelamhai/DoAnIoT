# Face Recognition Camera App

Ứng dụng nhận diện khuôn mặt realtime sử dụng Python với kiến trúc Clean Architecture.

## 🎯 Mục tiêu
- Nhận diện **Người thân / Người lạ** từ camera
- Lưu SQLite chỉ gồm: `name` + `time`
- Kiến trúc Clean Architecture (dễ bảo trì, mở rộng)

## 🚀 Quickstart

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

> **Lưu ý Windows**: Nếu gặp lỗi khi cài `face_recognition`, hãy dùng:
> - Anaconda/Miniconda, hoặc
> - Wheel file từ [tại đây](https://github.com/ageitgey/face_recognition/issues)

### 2. Test camera
```bash
python test_camera.py
```
Nhấn `q` để thoát. Nếu thấy hình ảnh từ camera → OK ✅

### 3. Thêm ảnh người thân
```
known_faces/
├── Linh/
│   ├── 01.jpg
│   ├── 02.jpg
│   └── 03.jpg
└── Nam/
    └── 01.jpg
```

**Lưu ý:**
- Mỗi người 1 folder (tên folder = tên hiển thị)
- 3-10 ảnh/người (nhiều góc + ánh sáng)
- Ảnh rõ mặt, không che khuất

### 4. Chạy ứng dụng

#### 🎥 Camera App (Realtime)
**Basic Mode (Phase 1):**
```bash
python run.py
```

**Advanced Mode (Phase 4 - InsightFace, Tracking, Multi-threading + Stranger Alerts):**
```bash
python run_advanced.py
```

Điều chỉnh trong [src/face_app/config/settings.py](src/face_app/config/settings.py):
- `USE_INSIGHTFACE = True` - Dùng InsightFace (chính xác hơn)
- `ENABLE_TRACKING = True` - Bật tracking (giảm compute)
- `USE_THREADED_CAMERA = True` - Multi-threading (FPS cao hơn)
- `ENABLE_ANTISPOOFING = True` - Anti-spoofing cơ bản
- `ENABLE_STRANGER_ALERTS = True` - Bật cảnh báo người lạ qua email

**Controls:**
- Nhấn `q` để thoát
- Nhấn `r` để reload known faces (thêm ảnh mới không cần restart)

#### 📊 Dashboard (Streamlit)

**Chạy dashboard:**
```bash
streamlit run dashboard.py
```

Mở trình duyệt tại: **http://localhost:8501**

**Tính năng Dashboard:**
- 📊 **Statistics Cards**: 
  - Tổng số events
  - Số người unique
  - Events hôm nay
  - Người được nhận diện nhiều nhất
  
- 📝 **Events Table**: 
  - Xem toàn bộ lịch sử recognition
  - Sắp xếp theo thời gian
  - Pagination
  
- 🔍 **Filters**: 
  - Filter theo tên người
  - Filter theo khoảng thời gian
  - Reset filters
  
- 📈 **Charts**: 
  - Biểu đồ events by person (bar chart)
  - Phân bố events theo thời gian
  
- 📥 **Export**: 
  - Download toàn bộ data dạng CSV
  - Export filtered data
  
- 🔄 **Auto-refresh**: 
  - Tự động refresh mỗi 5 giây
  - Toggle on/off

**Screenshots Dashboard:**
```
+----------------------------------------------------------+
|  Face Recognition Dashboard                              |
+----------------------------------------------------------+
|  [Total: 150]  [Unique: 3]  [Today: 45]  [Top: Linh]    |
+----------------------------------------------------------+
|  Filter by Name: [Dropdown▼]  Date Range: [From|To]     |
+----------------------------------------------------------+
|  Recognition Events Table                                |
|  | ID | Name     | Time                | Actions       |
|  | 1  | Linh     | 2026-01-11 12:30:00 | View         |
|  | 2  | Stranger | 2026-01-11 12:31:00 | View         |
+----------------------------------------------------------+
|  📊 Events by Person (Bar Chart)                         |
|  Linh:     ████████████████ 80                           |
|  Nam:      ████████ 40                                    |
|  Stranger: ████ 30                                        |
+----------------------------------------------------------+
|  📥 Download CSV    🔄 Auto-refresh: ON                  |
+----------------------------------------------------------+
```

**Troubleshooting Dashboard:**
- Nếu lỗi "streamlit command not found": `pip install streamlit`
- Nếu port 8501 đã được dùng: `streamlit run dashboard.py --server.port 8502`
- Không hiển thị data: Kiểm tra `data/attendance.sqlite` đã có dữ liệu chưa

#### 🌐 API Server (FastAPI)
```bash
python -m uvicorn api.main:app --reload
```
Truy cập API docs: http://localhost:8000/docs

## 📁 Cấu trúc dự án

```
DoAnIoT/
├── README.md
├── requirements.txt
├── test_camera.py          # Test camera
├── run.py                  # Main runner
├── dashboard.py            # Streamlit dashboard (Phase 3)
├── system.md               # Tài liệu kiến trúc chi tiết
├── known_faces/            # Ảnh người thân
│   ├── README.md
│   ├── Linh/
│   └── Nam/
├── data/
│   └── attendance.sqlite   # Database (auto-create)
├── api/                    # FastAPI server (Phase 3)
│   ├── main.py
│   └── models.py
└── src/
   └── face_app/
      ├── main.py           # Entry point
      ├── config/
      │  └── settings.py
      ├── domain/           # Entities, Ports, Policies
      ├── application/      # Use Cases
      ├── infrastructure/   # Adapters (Camera, Face Engine, SQLite)
      └── presentation/     # UI (OpenCV)
```

## 📋 Roadmap

### ✅ Phase 0 — Setup (Hoàn thành)
- [x] Cấu trúc dự án
- [x] requirements.txt
- [x] Test camera
- [x] Folder known_faces

### ✅ Phase 1 — MVP (Hoàn thành)
- [x] Face Recognition Engine
- [x] Load known faces
- [x] Match Policy
- [x] SQLite Repository
- [x] Recognize Frame Use Case
- [x] OpenCV UI

### ✅ Phase 3 — UI/Service (Hoàn thành)
- [x] Streamlit Dashboard
- [x] FastAPI REST API
- [x] Endpoints: /events, /stats, /recognize

### ✅ Phase 4 — Accuracy/Performance (Hoàn thành)
- [x] InsightFace engine (accurate & fast)
- [x] Face tracking (reduce compute)
- [x] Multi-threading (camera + recognition)
- [x] Basic anti-spoofing/liveness

### 🔮 Phase 2 — Testing (Tương lai)
- [x] Cache encodings (done in Phase 1)
- [x] Hot reload dataset (press 'r')
- [ ] Unit tests
- [ ] Integration tests

## 🛠️ Công nghệ

- **Computer Vision**: OpenCV
- **Face Recognition**: face_recognition (dlib), InsightFace (Phase 4)
- **Database**: SQLite
- **Web Framework**: FastAPI, Streamlit
- **Architecture**: Clean Architecture
- **Performance**: Multi-threading, Face Tracking

## 📚 Tài liệu

Chi tiết kiến trúc và design: xem [system.md](system.md)

## ⚙️ Cấu hình

Điều chỉnh trong [src/face_app/config/settings.py](src/face_app/config/settings.py):

**Basic Settings:**
- `TOLERANCE`: ngưỡng nhận diện (mặc định 0.5, InsightFace khuyến nghị 0.4)
- `COOLDOWN_SECONDS`: thời gian chống spam DB (mặc định 10s)
- `CAMERA_INDEX`: chỉ số camera (mặc định 0)
- `FRAME_WIDTH`: resize frame để xử lý nhanh hơn (mặc định 640)

**Phase 4 Advanced Settings:**
- `USE_INSIGHTFACE`: True = InsightFace (chính xác), False = dlib (mặc định False)
- `INSIGHTFACE_MODEL`: "buffalo_l" (chính xác) hoặc "buffalo_s" (nhanh)
- `ENABLE_TRACKING`: True = tracking giảm compute (mặc định False)
- `TRACK_DETECT_INTERVAL`: Detect mỗi N frames khi tracking (mặc định 5)
- `USE_THREADED_CAMERA`: True = multi-threading cho FPS cao hơn (mặc định False)
- `ENABLE_ANTISPOOFING`: True = bật anti-spoofing cơ bản (mặc định False)

**🚨 Stranger Alert Settings (NEW):**
- `ENABLE_STRANGER_ALERTS`: Bật/tắt cảnh báo người lạ (mặc định True)
- `STRANGER_TIME_WINDOW`: Cửa sổ thời gian theo dõi (mặc định 60 giây)
- `STRANGER_THRESHOLD`: Ngưỡng kích hoạt cảnh báo (mặc định 10 lần)
- `STRANGER_ALERT_COOLDOWN`: Thời gian chờ giữa các cảnh báo (mặc định 300 giây)

## 🚨 Tính năng Cảnh Báo Người Lạ

Hệ thống tự động giám sát và gửi email cảnh báo khi phát hiện nhiều người lạ trong thời gian ngắn.

### Cách hoạt động:
1. **Theo dõi liên tục**: Đếm số lần nhận diện "Stranger" trong 60 giây
2. **Kích hoạt cảnh báo**: Khi ≥ 10 lần → Gửi email cho người thân
3. **Tự động reset**: Nếu < 10 lần sau 60s → Reset về 0
4. **Chống spam**: Cooldown 5 phút giữa các email

### Cấu hình Email:

**Bước 1: Tạo App Password từ Gmail**
```
1. Bật 2-Factor Authentication: https://myaccount.google.com/security
2. Tạo App Password: https://myaccount.google.com/apppasswords
3. Copy mật khẩu 16 ký tự (không có khoảng trắng)
```

**Bước 2: Set biến môi trường (PowerShell)**
```powershell
$env:SENDER_EMAIL = "your_email@gmail.com"
$env:SENDER_PASSWORD = "your_app_password"  # App Password, NOT regular password!
$env:RECIPIENT_EMAILS = "family1@gmail.com,family2@gmail.com"
```

**Bước 3: Chạy app**
```bash
python run.py
```

**Chi tiết cấu hình:** Xem [docs/EMAIL_SETUP.md](docs/EMAIL_SETUP.md)

### Test Email:
```python
from face_app.infrastructure.notifications.email_service import EmailNotificationService
from datetime import datetime

service = EmailNotificationService(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    sender_email="your@gmail.com",
    sender_password="app_password",
    recipient_emails=["family@gmail.com"]
)

# Gửi email test
service.send_test_email()
```

### Hiển thị trên UI:
- **Camera App**: Hiển thị "Strangers: X/10" trên video
- **Console**: Thông báo khi gửi email thành công

## 📡 API Endpoints (Phase 3)

### FastAPI Server
Chạy server: `python -m uvicorn api.main:app --reload`

**Endpoints:**
- `GET /` - API info
- `GET /events?limit=100&name=Linh` - Lấy danh sách recognition events
- `GET /stats` - Thống kê (total, unique people, today, most frequent)
- `POST /recognize` - Nhận diện từ base64 image
- `POST /recognize/upload` - Nhận diện từ upload file
- `POST /reload` - Reload known faces

**API Docs:** http://localhost:8000/docs

### Streamlit Dashboard
Chạy: `streamlit run dashboard.py`

**Tính năng:**
- 📊 Thống kê realtime (total, unique, today, most frequent)
- 📝 Xem danh sách recognition events
- 🔍 Filter theo name & date
- 📈 Biểu đồ events by person
- 📥 Download CSV
- 🔄 Auto-refresh (5s)

## 📞 Hỗ trợ

Gặp vấn đề? Kiểm tra:
1. Camera hoạt động: `python test_camera.py`
2. Dependencies đã cài: `pip list | findstr "opencv face"`
3. Ảnh trong known_faces đúng format
4. SQLite file có quyền ghi
5. Email settings: Xem [docs/EMAIL_SETUP.md](docs/EMAIL_SETUP.md)

---

**Phiên bản**: 0.2.0 (MVP + Stranger Alerts)  
**Ngày**: 2026-01-09
