# Hardware Configuration Guide

## 📋 Quick Start Guide

### Option A: ESP32 (Recommended) - WiFi + MQTT

#### **Hardware Required:**
- ESP32 DevKit (hoặc compatible board)
- PIR HC-SR501 Motion Sensor
- Relay Module (3.3V hoặc 5V)
- Alarm/Speaker (hoặc LED để test)
- Breadboard + Jumper wires
- USB Cable (Micro USB hoặc USB-C tùy board)

#### **Software Required:**
- Arduino IDE 1.8.x hoặc 2.x
- ESP32 Board Support Package

---

## 🔧 Setup Instructions

### **Bước 1: Cài đặt Arduino IDE**

1. Download Arduino IDE từ: https://www.arduino.cc/en/software
2. Cài đặt ESP32 Board Support:
   - Mở Arduino IDE
   - File → Preferences
   - Thêm vào "Additional Board Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Tools → Board → Boards Manager
   - Tìm "esp32" và cài đặt "ESP32 by Espressif Systems"

3. Cài đặt thư viện cần thiết:
   - Sketch → Include Library → Manage Libraries
   - Cài các thư viện:
     - `PubSubClient` by Nick O'Leary (cho MQTT)

---

### **Bước 2: Đấu nối Hardware**

Xem chi tiết trong file: `hardware/schemas/wiring_diagram.txt`

**Kết nối cơ bản:**
```
PIR Sensor:
  VCC → 3.3V (ESP32)
  GND → GND (ESP32)
  OUT → GPIO27 (ESP32)

Relay Module:
  VCC → 3.3V hoặc 5V (ESP32)
  GND → GND (ESP32)
  IN  → GPIO26 (ESP32)
```

---

### **Bước 3: Cấu hình Code**

Mở file: `hardware/esp32/pir_mqtt_publisher.ino`

**Thay đổi các thông số sau:**

```cpp
// WiFi Credentials - THAY ĐỔI
const char* WIFI_SSID = "TenWiFiCuaBan";
const char* WIFI_PASSWORD = "MatKhauWiFi";

// MQTT Settings - THAY ĐỔI
const char* MQTT_BROKER = "test.mosquitto.org";  // Hoặc broker.hivemq.com
const char* MQTT_TOPIC = "iot/security/pir/nhom01";  // Thay nhom01
const char* MQTT_CLIENT_ID = "ESP32_PIR_001";
```

**Lưu ý:**
- `MQTT_TOPIC` phải **GIỐNG** với config trong `config/mqtt_config.yaml`
- `MQTT_BROKER` nên dùng:
  - `test.mosquitto.org` (public, free)
  - `broker.hivemq.com` (public, free)
  - Hoặc local broker nếu đã cài Mosquitto

---

### **Bước 4: Upload Code lên ESP32**

1. Kết nối ESP32 với PC qua USB
2. Chọn Board:
   - Tools → Board → ESP32 Arduino → **ESP32 Dev Module**
3. Chọn Port:
   - Tools → Port → **COMx** (Windows) hoặc **/dev/ttyUSBx** (Linux)
4. Upload:
   - Sketch → Upload (hoặc Ctrl+U)
   - Đợi "Done uploading" message

---

### **Bước 5: Kiểm tra hoạt động**

1. **Mở Serial Monitor:**
   - Tools → Serial Monitor
   - Set baud rate: **115200**

2. **Quan sát output:**
   ```
   =================================
   ESP32 IoT Security System
   =================================
   ✓ GPIO pins configured
   Connecting to WiFi: TenWiFi
   ✓ WiFi connected!
     IP Address: 192.168.1.100
   ✓ NTP time configured
   ✓ System ready!
   
   🟢 No motion
   📤 Published: {"timestamp":"2026-01-06T10:00:00Z","motion":0,...}
   ```

3. **Test chuyển động:**
   - Vẫy tay trước PIR sensor
   - Xem message: `🔴 MOTION DETECTED!`
   - Relay nên bật (LED/alarm kêu)

---

## 🐛 Troubleshooting

### **WiFi không kết nối:**
```
Symptom: WiFi connecting... (stuck)
Solution:
  ✓ Kiểm tra SSID và password đúng
  ✓ ESP32 chỉ hỗ trợ WiFi 2.4GHz (KHÔNG hỗ trợ 5GHz)
  ✓ Thử router khác hoặc hotspot điện thoại
  ✓ Reset ESP32 (nút BOOT + EN)
```

### **MQTT không kết nối:**
```
Symptom: Failed! RC=-2 hoặc RC=-4
Solution:
  ✓ Kiểm tra broker address đúng
  ✓ Test broker bằng MQTT Explorer (Windows app)
  ✓ Thử broker khác: broker.hivemq.com
  ✓ Kiểm tra firewall (nếu dùng local broker)
```

### **PIR sensor không phát hiện:**
```
Symptom: Motion luôn = 0
Solution:
  ✓ Đợi 30s sau khi cấp nguồn (PIR warm-up)
  ✓ Kiểm tra OUT pin nối đúng GPIO27
  ✓ Điều chỉnh potentiometer trên PIR (sensitivity)
  ✓ Test PIR bằng multimeter (OUT = 3.3V khi có motion)
```

### **Relay không bật:**
```
Symptom: Không nghe alarm kêu
Solution:
  ✓ Kiểm tra relay module cần 3.3V hay 5V
  ✓ Nếu cần 5V → nối VCC relay vào VIN pin (không phải 3.3V)
  ✓ Test relay bằng code riêng:
    digitalWrite(RELAY_PIN, HIGH);
    delay(1000);
    digitalWrite(RELAY_PIN, LOW);
```

---

## 📊 Testing với Backend

### **Test MQTT Messages:**

1. **Chạy MQTT Subscriber trên PC:**
   ```bash
   python scripts/mqtt_test_subscriber.py
   ```

2. **Vẫy tay trước PIR:**
   - Xem message xuất hiện trên console
   - Verify JSON format đúng

3. **Kiểm tra topic:**
   - ESP32 publish topic: `iot/security/pir/nhom01`
   - Python subscribe topic: `iot/security/pir/nhom01`
   - **PHẢI GIỐNG NHAU**

---

## 🔄 Option B: Arduino (Serial Mode)

Nếu không có ESP32, dùng Arduino Uno với Serial Bridge:

### **Setup:**

1. Upload file: `hardware/arduino/pir_serial.ino`
2. Chọn Board: **Arduino Uno**
3. Upload code

### **Chạy Serial Bridge:**

1. **List serial ports:**
   ```bash
   python backend/services/serial_bridge.py --list
   ```

2. **Chạy bridge:**
   ```bash
   python backend/services/serial_bridge.py --port COM3
   ```

3. **Verify:**
   - Serial Bridge đọc JSON từ Arduino
   - Publish lên MQTT broker
   - Test bằng subscriber script

---

## ✅ Verification Checklist

Trước khi chuyển sang Phase 4, kiểm tra:

- [ ] ESP32/Arduino upload thành công
- [ ] WiFi kết nối (với ESP32)
- [ ] PIR sensor phát hiện chuyển động
- [ ] Relay bật/tắt đúng
- [ ] MQTT messages publish lên broker
- [ ] Python subscriber nhận được messages
- [ ] JSON format đúng (`{"timestamp":"...", "motion":0/1}`)

---

## 📞 Support

Nếu gặp vấn đề:

1. Kiểm tra Serial Monitor output
2. Xem file `wiring_diagram.txt`
3. Test từng component riêng lẻ
4. Dùng multimeter kiểm tra voltage

---

**Last Updated:** January 6, 2026  
**Version:** 1.0
