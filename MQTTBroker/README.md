# Hướng dẫn MQTT với Python - Ngày 1 & 2

## 📋 Mục tiêu
- **Ngày 1**: Hiểu MQTT, topic, pub/sub và cài đặt môi trường
- **Ngày 2**: Test MQTT với Python, gửi lệnh ON/OFF điều khiển relay

## 🔧 Đã cài đặt
- ✅ Python virtual environment (.venv)
- ✅ paho-mqtt library
- ✅ MQTT Subscriber
- ✅ MQTT Publisher

## 📁 Cấu trúc File

```
DoAnIoT/
├── mqtt_subscriber.py   # Nhận lệnh ON/OFF
├── mqtt_publisher.py    # Gửi lệnh ON/OFF
└── README.md           # File hướng dẫn này
```

## 🚀 Hướng dẫn sử dụng

### Bước 1: Chạy Subscriber (Terminal 1)
Mở terminal đầu tiên và chạy:
```bash
C:/Users/ADMIN/Documents/PTIT/HK5/IoT/Project/DoAnIoT/.venv/Scripts/python.exe mqtt_subscriber.py
```

Subscriber sẽ:
- Kết nối tới MQTT broker (broker.hivemq.com)
- Subscribe topic: `iot/ptit/relay`
- Lắng nghe và hiển thị các message nhận được
- Xử lý lệnh ON/OFF

### Bước 2: Chạy Publisher (Terminal 2)
Mở terminal thứ hai và chạy:
```bash
C:/Users/ADMIN/Documents/PTIT/HK5/IoT/Project/DoAnIoT/.venv/Scripts/python.exe mqtt_publisher.py
```

Publisher cho phép:
- Nhập lệnh: `ON` hoặc `OFF`
- Gửi lệnh tới topic: `iot/ptit/relay`
- Nhập `exit` để thoát

### Bước 3: Test gửi/nhận
1. Trong terminal Publisher, nhập: `ON`
2. Kiểm tra terminal Subscriber xem có nhận được message không
3. Thử tiếp với lệnh `OFF`

## 📡 Thông tin MQTT

- **Broker**: broker.hivemq.com (public broker)
- **Port**: 1883
- **Topic**: iot/ptit/relay
- **Protocol**: MQTT v3.1.1

## 💡 Giải thích MQTT

### Publisher (Người gửi)
- Gửi message tới một topic cụ thể
- Không cần biết ai sẽ nhận
- Ví dụ: Gửi lệnh "ON" tới topic "iot/ptit/relay"

### Subscriber (Người nhận)
- Subscribe (đăng ký) một hoặc nhiều topic
- Nhận tất cả message được gửi tới topic đó
- Ví dụ: Subscribe "iot/ptit/relay" để nhận lệnh điều khiển

### Topic
- Đường dẫn phân cấp để phân loại message
- Sử dụng dấu `/` để phân cấp
- Ví dụ: `iot/ptit/relay`, `iot/ptit/sensor/pir`

### Broker
- Máy chủ trung gian
- Nhận message từ publisher và chuyển tới subscriber
- Đảm bảo message được gửi đúng người

## 🎯 Kết quả mong đợi

Khi chạy thành công:
```
[Terminal 1 - Subscriber]
✓ Kết nối MQTT Broker thành công!
✓ Đã subscribe topic: iot/ptit/relay
📡 Đang lắng nghe messages...

📩 Nhận được message:
   Topic: iot/ptit/relay
   Payload: ON
   Time: 14:30:15
   ➜ Relay: BẬT 💡

[Terminal 2 - Publisher]
Nhập lệnh (ON/OFF/exit): ON
📤 Đã gửi: ON
   Topic: iot/ptit/relay
   Time: 14:30:15
   ➜ Lệnh: BẬT relay 💡
```

## 🔍 Troubleshooting

### Không kết nối được broker
- Kiểm tra kết nối internet
- Thử broker khác: `test.mosquitto.org`
- Thay đổi trong code: `BROKER = "test.mosquitto.org"`

### Module not found: paho
```bash
C:/Users/ADMIN/Documents/PTIT/HK5/IoT/Project/DoAnIoT/.venv/Scripts/python.exe -m pip install paho-mqtt
```

### Subscriber không nhận được message
- Đảm bảo cả 2 chương trình dùng cùng broker
- Kiểm tra topic có khớp nhau không
- Chạy subscriber trước, sau đó mới chạy publisher

## 📝 Ghi chú

- Sử dụng public broker (broker.hivemq.com) nên không cần cài Mosquitto local
- Sau này có thể chuyển sang broker local khi deploy
- Topic có thể thay đổi tùy ý trong code
- QoS mặc định = 0 (gửi 1 lần, không đảm bảo nhận được)

## ➡️ Tiếp theo

- **Ngày 3**: ESP32 publish dữ liệu PIR
- **Ngày 4**: Server subscribe dữ liệu PIR
- **Ngày 5**: Server điều khiển relay qua ESP32

---
**Hoàn thành**: Ngày 1 & 2 ✅
