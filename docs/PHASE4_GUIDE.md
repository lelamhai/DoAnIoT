# Phase 4 - Performance & Accuracy Guide

## 🚀 Tổng quan

Phase 4 nâng cấp hệ thống với các tính năng:
- **InsightFace Engine**: Chính xác & nhanh hơn dlib
- **Face Tracking**: Giảm compute bằng tracking thay vì detect mọi frame
- **Multi-threading**: Camera capture & recognition song song
- **Anti-spoofing**: Phát hiện ảnh giả/video (cơ bản)

---

## 📦 Cài đặt

### 1. Dependencies
```bash
pip install insightface onnxruntime scipy
```

**GPU (tùy chọn):**
```bash
pip install onnxruntime-gpu
```

### 2. Download InsightFace models
Lần chạy đầu tiên, InsightFace sẽ tự động download models (~200MB).

---

## ⚙️ Cấu hình

Mở [src/face_app/config/settings.py](../src/face_app/config/settings.py):

### InsightFace
```python
USE_INSIGHTFACE = True  # Bật InsightFace
INSIGHTFACE_MODEL = "buffalo_l"  # buffalo_l (chính xác) hoặc buffalo_s (nhanh)
INSIGHTFACE_CTX_ID = -1  # -1 = CPU, 0 = GPU device 0
TOLERANCE = 0.4  # InsightFace dùng 0.4, dlib dùng 0.5
```

### Face Tracking
```python
ENABLE_TRACKING = True  # Bật tracking
TRACK_DETECT_INTERVAL = 5  # Detect đầy đủ mỗi 5 frames
TRACK_MAX_DISAPPEARED = 10  # Xóa track sau 10 frames
TRACK_IOU_THRESHOLD = 0.3  # IoU threshold cho matching
```

### Multi-threading
```python
USE_THREADED_CAMERA = True  # Bật threaded camera
CAMERA_BUFFER_SIZE = 2  # Buffer size (nhỏ = ít delay)
```

### Anti-spoofing
```python
ENABLE_ANTISPOOFING = True  # Bật anti-spoofing
ANTISPOOFING_MOTION_THRESHOLD = 2.0  # Ngưỡng motion
ANTISPOOFING_TEXTURE_THRESHOLD = 10.0  # Ngưỡng texture
```

---

## 🎯 So sánh Performance

### Dlib (face_recognition) vs InsightFace

| Metric | Dlib | InsightFace |
|--------|------|-------------|
| Accuracy | Good (96%) | Excellent (99%+) |
| Speed (CPU) | ~3 FPS | ~5-8 FPS |
| Speed (GPU) | N/A | ~20-30 FPS |
| Model Size | ~100MB | ~200MB |
| Encoding | 128-dim | 512-dim |

### Tracking OFF vs ON

| Mode | FPS | CPU Usage |
|------|-----|-----------|
| No Tracking | 3-5 | 80-100% |
| With Tracking | 10-15 | 30-50% |

### Threaded vs Non-threaded

| Mode | FPS | Latency |
|------|-----|---------|
| Single-thread | 3-5 | High |
| Multi-thread | 8-12 | Low |

---

## 🏃 Chạy

### Basic Mode (Phase 1)
```bash
python run.py
```

### Advanced Mode (Phase 4)
```bash
python run_advanced.py
```

---

## 🔧 Troubleshooting

### InsightFace không cài được
```bash
# Try with specific version
pip install insightface==0.7.3

# Or use conda
conda install -c conda-forge insightface
```

### GPU không hoạt động
```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Install GPU version
pip install onnxruntime-gpu
```

### FPS thấp
1. Bật `ENABLE_TRACKING = True`
2. Bật `USE_THREADED_CAMERA = True`
3. Giảm `FRAME_WIDTH` xuống 480
4. Dùng `INSIGHTFACE_MODEL = "buffalo_s"`

---

## 📊 Anti-spoofing

**Phương pháp:**
1. **Texture Analysis**: Ảnh in có texture variance thấp hơn
2. **Motion Detection**: Ảnh tĩnh không có motion tự nhiên
3. **Face Quality**: Kiểm tra brightness, sharpness

**Limitations:**
- Chỉ là phương pháp cơ bản
- Có thể bị bypass bằng video
- Production nên dùng model chuyên dụng (Silent Face Anti-Spoofing)

---

## 🎓 Best Practices

1. **Development**: Dùng dlib (đơn giản)
2. **Production với CPU**: Dùng InsightFace + Tracking
3. **Production với GPU**: Dùng InsightFace + Multi-threading
4. **High Security**: Thêm anti-spoofing model chuyên dụng

---

**Created:** Phase 4  
**Version:** 1.0.0
