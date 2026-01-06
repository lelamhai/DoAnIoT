# 🚀 IoT SECURITY MONITORING - PHIÊN BẢN ĐƠN GIẢN

Hệ thống giám sát an ninh IoT với 3 module độc lập, dễ sử dụng.

---

## ⚡ QUICK START (3 BƯỚC)

### **1. Train AI Model** (Chạy 1 lần đầu)
```bash
python 1_TRAIN_MODEL.py
```

### **2. Chạy Backend** (Terminal 1)
```bash
python 2_BACKEND.py
```

### **3. Chạy Dashboard** (Terminal 2)
```bash
python 3_FRONTEND.py
```

Mở browser: `http://localhost:8501`

---

## 📦 CÀI ĐẶT

```bash
pip install paho-mqtt pandas numpy scikit-learn streamlit plotly pyyaml
python scripts/setup_database.py
python 1_TRAIN_MODEL.py
```

---

## 🎯 3 MODULE CHÍNH

| Module | File | Nhiệm vụ |
|--------|------|----------|
| **1. Train AI** | `1_TRAIN_MODEL.py` | Train model khi đổi config thời gian |
| **2. Backend** | `2_BACKEND.py` | Nhận MQTT → Lưu Database |
| **3. Frontend** | `3_FRONTEND.py` | Hiển thị dashboard |

---

## ⚙️ ĐỔI THỜI GIAN SUSPICIOUS

1. Sửa: `config/time_config.yaml`
2. Chạy: `python 1_TRAIN_MODEL.py`
3. Restart: `python 2_BACKEND.py`

**Config hiện tại:** 15h-18h = SUSPICIOUS

---

## 📁 CẤU TRÚC PROJECT

```
DoAnIoT/
├── 1_TRAIN_MODEL.py          ← MODULE 1: Train AI
├── 2_BACKEND.py               ← MODULE 2: Backend
├── 3_FRONTEND.py              ← MODULE 3: Dashboard
│
├── config/
│   └── time_config.yaml       ← Config thời gian
│
├── backend/
│   └── simple_main.py         ← Backend chính
│
├── frontend/
│   └── app.py                 ← Dashboard
│
├── ai_model/
│   ├── data_generator.py
│   └── models/
│       └── classifier.pkl     ← AI model
│
├── data/
│   └── security.db            ← Database
│
└── logs/
    └── events.csv             ← CSV logs
```

---

## 🔄 LUỒNG DỮ LIỆU

```
ESP32 (PIR Sensor)
      ↓
MQTT Broker
      ↓
Backend (2_BACKEND.py)
      ↓
Database + CSV
      ↓
Dashboard (3_FRONTEND.py)
```

---

## 📖 Tài liệu chi tiết

- [README_SIMPLE.md](README_SIMPLE.md) - Hướng dẫn đầy đủ
- [system.md](system.md) - Kiến trúc hệ thống
- [Đề bài gốc](README_ORIGINAL.md)

---

**Version:** 2.0 - Simplified  
**Date:** January 6, 2026
