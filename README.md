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

**Advanced Mode (Phase 4 - InsightFace, Tracking, Multi-threading):**
```bash
python run_advanced.py
```

Điều chỉnh trong [src/face_app/config/settings.py](src/face_app/config/settings.py):
- `USE_INSIGHTFACE = True` - Dùng InsightFace (chính xác hơn)
- `ENABLE_TRACKING = True` - Bật tracking (giảm compute)
- `USE_THREADED_CAMERA = True` - Multi-threading (FPS cao hơn)
- `ENABLE_ANTISPOOFING = True` - Anti-spoofing cơ bản

#### Dashboard (Streamlit)
```bash
streamlit run dashboard.py
```

#### API Server (FastAPI)
```bash
python -m uvicorn api.main:app --reload
```
Truy cập: http://localhost:8000/docs

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

---

**Phiên bản**: 0.1.0 (MVP - Phase 0)  
**Ngày**: 2026-01-09
