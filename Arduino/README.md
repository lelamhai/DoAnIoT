# ESP32 MQTT Publisher - Arduino

## 📝 Mô tả
Script Arduino cho ESP32 thay thế `mqtt_publisher.py`. Gửi lệnh ON/OFF qua MQTT bằng nút nhấn vật lý.

## 🔧 Yêu cầu phần cứng
- ESP32 DevKit
- 2 nút nhấn (tactile switch)
- 2 điện trở 10kΩ (tùy chọn - nếu không dùng INPUT_PULLUP)
- Dây jumper
- Breadboard

## 📐 Sơ đồ kết nối

```
ESP32                  Nút nhấn ON
GPIO 25 ────────────── Nút nhấn ──── GND
GPIO 26 ────────────── Nút nhấn ──── GND (Nút OFF)
GPIO 2  ────────────── LED built-in (báo trạng thái)
```

### Chi tiết kết nối:
- **Nút ON**: GPIO 25 → Nút nhấn → GND
- **Nút OFF**: GPIO 26 → Nút nhấn → GND  
- **LED**: GPIO 2 (LED built-in trên ESP32)

*Lưu ý: Sử dụng INPUT_PULLUP nên không cần điện trở kéo lên ngoài*

## 📚 Thư viện cần cài

### Trong Arduino IDE:
1. **WiFi** (built-in ESP32)
2. **PubSubClient** - MQTT client
   - Vào: Sketch → Include Library → Manage Libraries
   - Tìm: "PubSubClient" by Nick O'Leary
   - Cài đặt phiên bản mới nhất

## ⚙️ Cấu hình

### 1. Cấu hình WiFi (dòng 16-17)
```cpp
const char* ssid = "YOUR_WIFI_SSID";        // Thay tên WiFi của bạn
const char* password = "YOUR_WIFI_PASSWORD"; // Thay mật khẩu WiFi
```

### 2. Cấu hình MQTT (dòng 20-23)
```cpp
const char* mqtt_broker = "broker.hivemq.com";  // Giữ nguyên hoặc đổi broker
const int mqtt_port = 1883;
const char* mqtt_topic = "iot/ptit/relay";      // Phải khớp với subscriber
const char* mqtt_client_id = "ESP32_Publisher";
```

### 3. Cấu hình GPIO (dòng 26-28)
```cpp
const int BUTTON_ON_PIN = 25;   // Có thể đổi GPIO khác
const int BUTTON_OFF_PIN = 26;  // Có thể đổi GPIO khác
const int LED_PIN = 2;          // LED built-in
```

## 🚀 Hướng dẫn sử dụng

### Bước 1: Mở Arduino IDE
- File → Open → Chọn `esp32_publisher.ino`

### Bước 2: Cấu hình Board
- Tools → Board → ESP32 Arduino → ESP32 Dev Module
- Tools → Port → Chọn COM port của ESP32

### Bước 3: Sửa thông tin WiFi
- Thay `YOUR_WIFI_SSID` và `YOUR_WIFI_PASSWORD`

### Bước 4: Upload code
- Nhấn nút Upload (→) hoặc Ctrl+U
- Đợi compile và upload hoàn tất

### Bước 5: Mở Serial Monitor
- Tools → Serial Monitor
- Chọn baud rate: **115200**

### Bước 6: Test
1. Chạy Python subscriber trên máy tính:
   ```bash
   python mqtt_subscriber.py
   ```
2. Nhấn nút GPIO 25 trên ESP32 → Gửi ON
3. Nhấn nút GPIO 26 trên ESP32 → Gửi OFF
4. Kiểm tra subscriber nhận được message

## 📊 Output Serial Monitor

```
================================================
      ESP32 MQTT Publisher - Điều khiển Relay
================================================

🔌 Đang kết nối WiFi: MyWiFi
.....
✓ Kết nối WiFi thành công!
   IP Address: 192.168.1.100
   Signal: -45 dBm

🔄 Đang kết nối MQTT Broker... ✓ Thành công!
   Broker: broker.hivemq.com:1883

📡 Hệ thống sẵn sàng!
   - Nhấn nút GPIO 25 để gửi ON
   - Nhấn nút GPIO 26 để gửi OFF
================================================

🔘 Phát hiện nhấn nút ON

================================================
📤 Đã gửi: ON
   Topic: iot/ptit/relay
   Time: 15
   ➜ Lệnh: BẬT relay 💡
================================================
```

## 🔍 Troubleshooting

### WiFi không kết nối được
- Kiểm tra SSID và password đúng chưa
- Kiểm tra ESP32 trong vùng phủ sóng WiFi
- Thử reset ESP32 (nút EN)

### MQTT không kết nối được
- Kiểm tra kết nối internet
- Thử đổi broker: `test.mosquitto.org`
- Kiểm tra firewall

### Nút nhấn không hoạt động
- Kiểm tra kết nối nút nhấn
- Kiểm tra GPIO pin đúng không
- Test bằng Serial Monitor

### Subscriber không nhận được message
- Kiểm tra topic khớp nhau chưa
- Kiểm tra cả 2 dùng cùng broker
- Chạy subscriber trước khi test ESP32

## 💡 So sánh với Python Publisher

| Tính năng | Python Publisher | ESP32 Publisher |
|-----------|-----------------|----------------|
| Input | Keyboard (console) | Nút nhấn vật lý |
| Kết nối | WiFi/LAN máy tính | WiFi ESP32 |
| Độ trễ | Thấp | Rất thấp |
| Sử dụng | Test trên máy | Triển khai thực tế |
| Nguồn điện | USB máy tính | 5V/3.3V độc lập |
| Chi phí | Miễn phí | ~50-100k VNĐ |

## ⚡ Tính năng

- ✅ Kết nối WiFi tự động
- ✅ Tự động kết nối lại MQTT khi mất kết nối
- ✅ Chống dội nút nhấn (debounce 200ms)
- ✅ LED báo hiệu trạng thái
- ✅ Serial Monitor hiển thị chi tiết
- ✅ Tương thích với Python subscriber

## 📝 Ghi chú

- Code sử dụng `INPUT_PULLUP` nên nút nhấn nối trực tiếp GPIO → GND
- LED built-in (GPIO 2) sáng khi gửi ON, tắt khi gửi OFF
- Debounce 200ms để tránh gửi nhiều lần khi nhấn 1 lần
- QoS = 0 (giống Python publisher)

## ➡️ Bước tiếp theo

Kết hợp với:
- Python subscriber để nhận lệnh
- Relay module để điều khiển thiết bị thật
- PIR sensor để phát hiện chuyển động (Ngày 3)

---
**Thay thế**: mqtt_publisher.py → esp32_publisher.ino ✅
