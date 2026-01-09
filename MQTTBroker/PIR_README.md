# PIR Sensor MQTT Subscriber - Python

## 📝 Mô tả
Subscriber Python để nhận dữ liệu từ ESP32 PIR sensor qua MQTT. Hiển thị cảnh báo khi phát hiện chuyển động.

## 🎯 Mục đích
- **Ngày 3-4**: ESP32 publish dữ liệu PIR, Server subscribe và hiển thị
- Nhận message "motion" / "no_motion" từ ESP32
- Đếm số lần phát hiện chuyển động
- Hiển thị thời gian phát hiện

## 📡 Cấu hình MQTT

### ESP32 (Publisher):
- **Broker**: broker.hivemq.com
- **Port**: 1883
- **Topic**: iot/nhom03/security/pir
- **Client ID**: ESP32_SERCURITY
- **Messages**: "motion", "no_motion", "online"

### Python (Subscriber):
- **Broker**: broker.hivemq.com (khớp với ESP32)
- **Port**: 1883 (khớp với ESP32)
- **Topic**: iot/nhom03/security/pir (khớp với ESP32)
- **Client ID**: Python_PIR_Subscriber

## 🚀 Sử dụng

### Bước 1: Upload code ESP32
```cpp
// Upload esp32_publisher.ino lên ESP32
// Đảm bảo PIR sensor kết nối GPIO27
```

### Bước 2: Chạy Subscriber
```bash
# Activate virtual environment (nếu cần)
.venv\Scripts\activate

# Chạy PIR subscriber
python MQTTBroker/pir_subscriber.py
```

### Bước 3: Test
1. Di chuyển tay trước PIR sensor
2. Xem output trên Python subscriber
3. Kiểm tra số lần phát hiện

## 📊 Output mẫu

```
============================================================
        ESP32 PIR SENSOR - MQTT SUBSCRIBER
============================================================
🔌 Đang kết nối tới MQTT Broker...
   Broker: broker.hivemq.com:1883
   Client ID: Python_PIR_Subscriber

✓ Kết nối MQTT Broker thành công!
✓ Đã subscribe topic: iot/nhom03/security/pir
✓ Subscribe thành công với QoS: 0

📡 Đang lắng nghe PIR sensor...
   🎯 Chờ ESP32 phát hiện chuyển động...
   ⌨️  Nhấn Ctrl+C để dừng
============================================================

============================================================
📡 [14:30:15] Nhận từ ESP32:
   Topic: iot/nhom03/security/pir
   Payload: online
   🟢 ESP32 đã kết nối và sẵn sàng
   📍 PIR sensor đang hoạt động
============================================================

============================================================
📡 [14:30:42] Nhận từ ESP32:
   Topic: iot/nhom03/security/pir
   Payload: motion
   🚨 PHÁT HIỆN CHUYỂN ĐỘNG!
   📊 Tổng số lần phát hiện: 1
   ⚡ CẢNH BÁO: Có người di chuyển!
============================================================

============================================================
📡 [14:30:45] Nhận từ ESP32:
   Topic: iot/nhom03/security/pir
   Payload: no_motion
   ✓ Không có chuyển động
   ⏱️  Thời gian kể từ lần cuối: 3.2s
============================================================

^C
============================================================
⏹️  DỪNG SUBSCRIBER
📊 Tổng số lần phát hiện chuyển động: 1
🕐 Lần cuối phát hiện: 14:30:42
============================================================
✓ Đã ngắt kết nối
```

## 🔍 Các message từ ESP32

| Message | Ý nghĩa | Khi nào |
|---------|---------|---------|
| `online` | ESP32 kết nối | Khi ESP32 start up |
| `motion` | Phát hiện chuyển động | PIR = HIGH |
| `no_motion` | Không có chuyển động | PIR = LOW |

## 📈 Tính năng

- ✅ Hiển thị thời gian thực
- ✅ Đếm số lần phát hiện chuyển động
- ✅ Tính thời gian giữa các lần phát hiện
- ✅ Cảnh báo rõ ràng khi có motion
- ✅ Thống kê khi thoát (Ctrl+C)
- ✅ Tương thích 100% với ESP32 code

## 🔧 So sánh với mqtt_subscriber.py

| Tính năng | mqtt_subscriber.py | pir_subscriber.py |
|-----------|-------------------|-------------------|
| Mục đích | Đa năng (PIR + Relay) | Chuyên PIR |
| Đếm motion | ❌ | ✅ |
| Thời gian | Hiển thị | Tính toán khoảng cách |
| Cảnh báo | Đơn giản | Chi tiết, nổi bật |
| Thống kê | ❌ | ✅ |
| Sử dụng | Test chung | Production PIR |

## 🛠️ Troubleshooting

### ESP32 không publish
- Kiểm tra Serial Monitor ESP32
- Đảm bảo WiFi connected
- Kiểm tra PIR sensor warm-up (30-60s)

### Subscriber không nhận
- Kiểm tra topic khớp: `iot/nhom03/security/pir`
- Kiểm tra broker khớp: `broker.hivemq.com`
- Chạy subscriber trước khi test ESP32

### PIR không phát hiện
- Đợi PIR warm-up 30-60 giây
- Kiểm tra kết nối PIR OUT → GPIO27
- Kiểm tra nguồn PIR (VCC, GND)
- Di chuyển gần PIR hơn (1-3m)

## 💡 Mở rộng

### Lưu log vào file
```python
# Thêm vào on_message
with open("pir_log.txt", "a") as f:
    f.write(f"{current_time},{message}\n")
```

### Gửi cảnh báo email
```python
# Khi phát hiện motion
import smtplib
# Send email alert...
```

### Kết hợp với relay
```python
# Khi motion → bật đèn
if message == "motion":
    client.publish("iot/ptit/relay", "ON")
```

## ➡️ Roadmap

- ✅ Ngày 3: ESP32 publish PIR ← **Đã xong**
- ✅ Ngày 4: Server subscribe PIR ← **Đang làm**
- ⏳ Ngày 5: Server điều khiển relay tự động

---
**File**: pir_subscriber.py  
**Kết hợp với**: esp32_publisher.ino (Arduino/esp32_publisher.ino)  
**Hoàn thành**: Ngày 3-4 ✅
