# 🚀 QUICK START GUIDE - IoT Security System

Hướng dẫn nhanh để chạy hệ thống hoàn chỉnh.

---

## 📋 PREREQUISITES

✅ Python 3.12 installed  
✅ All packages installed (`pip install -r requirements.txt`)  
✅ ESP32 + PIR sensor (optional for full demo)

---

## ⚡ QUICK START (Software Only)

### 1. Start Backend (Terminal 1)
```bash
python backend/main.py
```

**Expected:**
```
==================================================
IoT SECURITY MONITORING SYSTEM - BACKEND
==================================================
  ✓ Database connected: data\security.db
  ✓ AI Service initialized
  ✓ Alert Service initialized
  ✓ System Monitor initialized
✅ Backend is running!
```

---

### 2. Start Dashboard (Terminal 2)
```bash
streamlit run frontend/app.py
```

**Opens in browser:** http://localhost:8501

---

### 3. Simulate Live Events (Terminal 3)
```bash
python scripts/test_live_dashboard.py
```

**Generates events every 5 seconds**

---

## 🔌 FULL DEMO (với Hardware)

### 1. Upload ESP32 Code
```bash
# Open Arduino IDE
# File → Open → arduino/arduino.ino
# Tools → Board → ESP32 Dev Module
# Tools → Port → COM3
# Click Upload
```

### 2. Start Backend
```bash
python backend/main.py
```

### 3. Start Dashboard
```bash
streamlit run frontend/app.py
```

### 4. Test PIR Sensor
Wave hand in front of sensor → See real-time updates!

---

## 🧪 TESTING

### Integration Test
```bash
# Terminal 1: Start backend first
python backend/main.py

# Terminal 2: Run tests
python scripts/test_integration.py
```

### System Monitor
```bash
python backend/infrastructure/system_monitor.py
```

---

## 📊 DEMO DATA

### Generate 24h Demo Data
```bash
python scripts/demo_dashboard.py
```

**Creates 288 realistic events**

---

## 🔔 CONFIGURE ALERTS

### Email Alerts (Gmail)
```powershell
$env:ALERT_EMAIL_ENABLED="true"
$env:SMTP_USERNAME="your_email@gmail.com"
$env:SMTP_PASSWORD="your_app_password"
$env:ALERT_RECIPIENTS="admin@example.com"

# Restart backend
python backend/main.py
```

### Telegram Alerts
```powershell
$env:TELEGRAM_ENABLED="true"
$env:TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
$env:TELEGRAM_CHAT_IDS="123456789"

# Restart backend
python backend/main.py
```

---

## 🐛 TROUBLESHOOTING

### Backend không kết nối MQTT
```bash
# Check internet connection
# Verify broker: test.mosquitto.org

# Try alternative broker:
# Edit backend/main.py line 98:
broker="broker.hivemq.com"
```

### Dashboard không hiển thị data
```bash
# Check database exists
ls data/security.db

# Generate demo data
python scripts/demo_dashboard.py

# Refresh dashboard (F5)
```

### ESP32 không upload
```bash
# Install CP2102 driver
# https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

# Hold BOOT button during upload
# Reduce upload speed: Tools → Upload Speed → 115200
```

---

## 📁 PROJECT STRUCTURE

```
DoAnIoT/
├── backend/
│   ├── main.py                    # ⭐ Start here
│   ├── services/
│   │   ├── mqtt_service.py
│   │   ├── ai_service.py
│   │   └── alert_service.py       # ⭐ Alerts
│   └── infrastructure/
│       ├── database.py
│       └── system_monitor.py      # ⭐ Monitoring
│
├── frontend/
│   └── app.py                     # ⭐ Dashboard
│
├── ai_model/
│   ├── train.py
│   └── models/
│       └── classifier.pkl         # ⭐ Trained model
│
├── arduino/
│   └── arduino.ino                # ⭐ ESP32 code
│
├── scripts/
│   ├── test_integration.py        # ⭐ Integration tests
│   ├── demo_dashboard.py          # ⭐ Generate demo data
│   └── test_live_dashboard.py     # ⭐ Live simulator
│
└── docs/
    ├── phase7_summary.md          # ⭐ Phase 7 docs
    └── esp32_hardware_guide.md    # ⭐ Hardware guide
```

---

## 🎯 COMMON TASKS

### Check System Health
```bash
# During backend runtime, press Ctrl+C
# Final health report will be displayed
```

### View Database
```bash
# Install SQLite browser or use Python:
python -c "from backend.infrastructure.database import Database; db = Database(); print(db.get_recent_events(5))"
```

### Export Events to CSV
```bash
# Events are auto-logged to: logs/events.csv
# Open with Excel or:
cat logs/events.csv
```

---

## 📞 SUPPORT

**Documentation:**
- Phase 7 Summary: `docs/phase7_summary.md`
- Hardware Guide: `docs/esp32_hardware_guide.md`
- System Architecture: `system.md`

**Testing:**
- Integration tests: `python scripts/test_integration.py`
- System monitor: `python backend/infrastructure/system_monitor.py`

---

## ✅ CHECKLIST

Before demo:
- [ ] Backend running
- [ ] Dashboard running
- [ ] Database has data
- [ ] Alerts configured (optional)
- [ ] ESP32 connected (optional)
- [ ] Screenshots ready

---

**Last Updated:** January 6, 2026  
**Version:** 1.0  
**Status:** Phase 7 Complete
