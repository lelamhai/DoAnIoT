# 🚀 IoT SECURITY MONITORING - 3 MODULE ĐƠN GIẢN

## 📁 CẤU TRÚC PROJECT

```
DoAnIoT/
├── 1_TRAIN_MODEL.py          # MODULE 1: Train AI (chạy khi đổi config)
├── 2_BACKEND.py               # MODULE 2: Backend đơn giản (lưu data)
├── 3_FRONTEND.py              # MODULE 3: Dashboard (hiển thị)
│
├── config/
│   └── time_config.yaml       # Config thời gian (15h-18h = Suspicious)
│
├── backend/                   # Backend services
│   ├── simple_main.py         # Backend entry point
│   ├── services/
│   │   ├── mqtt_service.py
│   │   ├── data_processor.py
│   │   └── feature_engineering.py
│   └── infrastructure/
│       ├── database.py
│       ├── logger.py
│       └── config.py
│
├── frontend/                  # Frontend dashboard
│   └── app.py
│
├── ai_model/                  # AI training
│   ├── data_generator.py
│   ├── train.py
│   ├── datasets/
│   └── models/
│       └── classifier.pkl     # Trained model
│
├── hardware/                  # ESP32/Arduino code
│   └── esp32/
│       └── pir_mqtt_publisher.ino
│
├── scripts/                   # Test scripts
│   ├── mqtt_test_publisher.py
│   ├── mqtt_test_subscriber.py
│   └── setup_database.py
│
├── data/                      # Database
│   └── security.db
│
└── logs/                      # CSV logs
    └── events.csv
```

---

## 🎯 3 MODULE CHÍNH

### **MODULE 1: TRAIN AI** 🤖
**File:** `train_model.py`

**Khi nào chạy:**
- Lần đầu setup project
- Khi thay đổi `config/time_config.yaml`

**Cách chạy:**
```bash
python train_model.py
```

**Kết quả:**
- Generate training data (500 samples)
- Train Random Forest model
- Lưu model: `ai_model/models/classifier.pkl`
- Accuracy: ~94%

---

### **MODULE 2: BACKEND** 💾
**File:** `backend/simple_main.py`

**Nhiệm vụ:**
- Nhận MQTT messages từ ESP32
- Lưu vào Database (SQLite)
- Lưu vào CSV logs

**Cách chạy:**
```bash
python backend/simple_main.py
```

**Output mẫu:**
```
[#1] 🔴 15:50:31
     Motion: 1 | Sensor: ESP32_NhomO3_HoangMinh
     ✓ Saved to DB
     ✓ Saved to CSV

[#2] ⚪ 15:50:33
     Motion: 0 | Sensor: ESP32_NhomO3_HoangMinh
     ✓ Saved to DB
     ✓ Saved to CSV
```

---

### **MODULE 3: FRONTEND** 📊
**File:** `frontend/app.py`

**Nhiệm vụ:**
- Hiển thị dữ liệu từ Database
- Real-time dashboard
- Charts và statistics

**Cách chạy:**
```bash
streamlit run frontend/app.py
```

**Truy cập:** `http://localhost:8501`

---

## 🚀 HƯỚNG DẪN SỬ DỤNG

### **Lần đầu setup:**

1. **Cài dependencies:**
```bash
pip install paho-mqtt pandas numpy scikit-learn streamlit plotly pyyaml
```

2. **Setup database:**
```bash
python scripts/setup_database.py
```

3. **Train model:**
```bash
python train_model.py
```

---

### **Chạy project:**

**Terminal 1 - Backend:**
```bash
python backend/simple_main.py
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/app.py
```

**Terminal 3 - Test (Optional):**
```bash
python scripts/mqtt_test_publisher.py
```

---

## ⚙️ THAY ĐỔI CONFIG THỜI GIAN

### **Bước 1: Sửa config**
File: `config/time_config.yaml`

```yaml
time_rules:
  suspicious_hours:
    start: 15  # Đổi thành thời gian bạn muốn
    end: 18    # Đổi thành thời gian bạn muốn
```

### **Bước 2: Train lại model**
```bash
python train_model.py
```

### **Bước 3: Restart backend**
```bash
# Dừng backend (Ctrl+C)
# Chạy lại:
python backend/simple_main.py
```

---

## 📊 LUỒNG DỮ LIỆU

```
ESP32 (PIR Sensor)
      ↓
MQTT Broker (broker.hivemq.com)
      ↓
Backend (simple_main.py)
      ↓
Database (security.db) + CSV (events.csv)
      ↓
Frontend (app.py) - Hiển thị dashboard
```

---

## 🔧 CÁC FILE QUAN TRỌNG

| File | Mô tả |
|------|-------|
| `train_model.py` | Train AI model |
| `backend/simple_main.py` | Backend chính |
| `frontend/app.py` | Dashboard |
| `config/time_config.yaml` | Config thời gian |
| `scripts/mqtt_test_publisher.py` | Test MQTT |
| `hardware/esp32/pir_mqtt_publisher.ino` | Code ESP32 |

---

## 📝 LOGIC THỜI GIAN HIỆN TẠI

**Config:** `config/time_config.yaml`
- **15h-18h:** SUSPICIOUS (chuyển động = cảnh báo)
- **Ngoài 15h-18h:** NORMAL (chuyển động = bình thường)

**Để đổi logic:** Sửa file config → Chạy `python train_model.py`

---

## ❓ TROUBLESHOOTING

### Backend không nhận MQTT?
```bash
# Check MQTT config
cat config/mqtt_config.yaml
```

### Frontend không hiển thị data?
- Kiểm tra backend đang chạy
- Kiểm tra database có data: `ls -l data/security.db`

### Model không chính xác?
- Chạy lại: `python train_model.py`
- Tăng số samples trong `data_generator.py`

---

**Version:** 2.0 - Simplified  
**Date:** January 6, 2026
