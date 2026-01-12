# ESP32 + PIR Sensor - MQTT Integration

## 📋 Mô tả

Code Arduino cho ESP32 kết nối với cảm biến PIR để điều khiển hệ thống nhận diện khuôn mặt qua MQTT.

## 🔌 Sơ đồ kết nối

```
PIR Sensor          ESP32
┌─────────┐       ┌─────────┐
│  VCC    │──────▶│  5V     │
│  OUT    │──────▶│ GPIO 13 │
│  GND    │──────▶│  GND    │
└─────────┘       └─────────┘
```

## ⚙️ Cấu hình

### 1. WiFi Settings (Dòng 18-19)
```cpp
const char* ssid = "YOUR_WIFI_SSID";        // Tên WiFi
const char* password = "YOUR_WIFI_PASSWORD"; // Mật khẩu WiFi
```

### 2. MQTT Settings (Đã cấu hình sẵn)
```cpp
const char* mqtt_server = "broker.hivemq.com";
const char* mqtt_topic = "iot/nhom03/security/pir";
```

### 3. GPIO Pin
```cpp
const int PIR_PIN = 13;  // GPIO 13 cho PIR
const int LED_PIN = 2;   // LED built-in (debug)
```

## 📦 Thư viện cần cài đặt

1. **PubSubClient** - MQTT library
   - Arduino IDE: `Sketch → Include Library → Manage Libraries → Search "PubSubClient" → Install`
   - Version: 2.8.0 hoặc mới hơn

2. **WiFi** - Built-in ESP32 library (không cần cài)

## 🚀 Hướng dẫn Upload Code

### Bước 1: Cấu hình Arduino IDE
1. Cài đặt ESP32 Board Manager:
   - `File → Preferences → Additional Board Manager URLs`
   - Thêm: `https://dl.espressif.com/dl/package_esp32_index.json`
2. `Tools → Board → Boards Manager → Search "ESP32" → Install`

### Bước 2: Chọn Board
- `Tools → Board → ESP32 Arduino → ESP32 Dev Module`
- `Tools → Upload Speed → 115200`
- `Tools → Port → COMx` (chọn port ESP32 của bạn)

### Bước 3: Sửa WiFi
```cpp
const char* ssid = "Ten_WiFi_Nha_Ban";
const char* password = "Mat_Khau_WiFi";
```

### Bước 4: Upload
- Nhấn nút `Upload` (hoặc `Ctrl+U`)
- Chờ "Done uploading"

### Bước 5: Mở Serial Monitor
- `Tools → Serial Monitor` (hoặc `Ctrl+Shift+M`)
- Chọn baud rate: `115200`

## 📊 Hoạt động

### Khi khởi động:
```
=================================
ESP32 PIR MQTT - Nhom 03
=================================
✅ GPIO configured
   PIR Pin: GPIO 13
   LED Pin: GPIO 2
📶 Connecting to WiFi...
   SSID: YourWiFi
✅ WiFi connected!
   IP Address: 192.168.1.100
📡 Connecting to MQTT broker...
✅ MQTT connected!
   Topic: iot/nhom03/security/pir
⏳ PIR warming up (30s)...
✅ PIR ready!
🚀 System Ready
```

### Khi phát hiện chuyển động:
```
─────────────────────────────────
📡 PIR State Changed: MOTION
📤 Published to MQTT: '1'
⏰ Time: 45230 ms
─────────────────────────────────
```

### Khi không còn chuyển động:
```
─────────────────────────────────
📡 PIR State Changed: NO MOTION
📤 Published to MQTT: '0'
⏰ Time: 48450 ms
─────────────────────────────────
```

## 🔍 Kiểm tra MQTT Message

### Online MQTT Client
1. Truy cập: http://www.hivemq.com/demos/websocket-client/
2. Click "Connect"
3. Subscribe to topic: `iot/nhom03/security/pir`
4. Quan sát message "0" và "1"

### Python Test Script
```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"PIR: {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883)
client.subscribe("iot/nhom03/security/pir")
client.loop_forever()
```

## 🐛 Troubleshooting

### WiFi không kết nối được
- Kiểm tra SSID và password
- Đảm bảo WiFi là 2.4GHz (ESP32 không hỗ trợ 5GHz)
- Thử đặt ESP32 gần router

### MQTT không kết nối
- Kiểm tra internet connection
- Thử ping `broker.hivemq.com`
- Kiểm tra firewall

### PIR không hoạt động
- Kiểm tra kết nối GPIO 13
- Đợi 30 giây warm-up
- Thử điều chỉnh sensitivity trimpot trên PIR

### LED không sáng
- LED built-in ở GPIO 2
- Một số board ESP32 không có LED built-in
- Có thể bỏ qua lỗi này

## 📝 Technical Details

### Debounce Logic
- Debounce time: 500ms
- Tránh false trigger do nhiễu

### Publish Strategy
- **On Change**: Gửi ngay khi PIR thay đổi trạng thái
- **Heartbeat**: Gửi mỗi 1 giây để maintain state

### PIR Warm-up
- 30 giây warm-up time
- PIR cần ổn định trước khi hoạt động

## 🔗 Integration với Python App

ESP32 gửi message → MQTT Broker → Python App nhận:
```
PIR = "1" → active = True  → Ghi DB + Email
PIR = "0" → active = False → Chỉ hiển thị
```

## 📌 Lưu ý

1. **WiFi ổn định**: Đảm bảo ESP32 gần router
2. **Power supply**: Dùng USB 5V/1A trở lên
3. **PIR sensitivity**: Điều chỉnh trimpot nếu cần
4. **MQTT QoS**: Mặc định QoS 0 (fire and forget)

## 🎯 Tương lai

- [ ] Thêm WiFi Manager (không cần hard-code SSID)
- [ ] Thêm OTA (Over-The-Air) update
- [ ] Thêm Deep Sleep mode để tiết kiệm pin
- [ ] Thêm MQTT authentication
