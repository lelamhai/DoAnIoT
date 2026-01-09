import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

# Cấu hình MQTT - Khớp với ESP32
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_PIR = "iot/nhom03/security/pir"
CLIENT_ID = "Python_PIR_Subscriber"

# Biến đếm
motion_count = 0
last_motion_time = None

# Callback khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✓ Kết nối MQTT Broker thành công!")
        client.subscribe(TOPIC_PIR)
        print(f"✓ Đã subscribe topic: {TOPIC_PIR}")
    else:
        print(f"✗ Kết nối thất bại. Mã lỗi: {rc}")

# Callback khi nhận được message
def on_message(client, userdata, msg):
    global motion_count, last_motion_time
    
    message = msg.payload.decode()
    current_time = datetime.now().strftime('%H:%M:%S')
    
    print(f"\n{'='*60}")
    print(f"📡 [{current_time}] Nhận từ ESP32:")
    print(f"   Topic: {msg.topic}")
    print(f"   Raw Payload: {message}")
    
    # Parse JSON
    try:
        data = json.loads(message)
        
        # Hiển thị JSON parsed
        if "timestamp" in data:
            print(f"   🕐 Timestamp: {data['timestamp']}")
        
        # Xử lý motion field
        if "motion" in data:
            motion_value = data["motion"]
            
            if motion_value == 1:
                motion_count += 1
                last_motion_time = datetime.now()
                print(f"   🚨 PHÁT HIỆN CHUYỂN ĐỘNG!")
                print(f"   📊 Tổng số lần phát hiện: {motion_count}")
                
            elif motion_value == 0:
                print(f"   ✓ Không có chuyển động")
                if last_motion_time:
                    elapsed = (datetime.now() - last_motion_time).total_seconds()
                    print(f"   ⏱️  Thời gian kể từ lần cuối: {elapsed:.1f}s")
        
        # Xử lý status field (online message)
        elif "status" in data:
            if data["status"] == "online":
                print(f"   🟢 ESP32 đã kết nối và sẵn sàng")
                print(f"   📍 PIR sensor đang hoạt động")
        
        else:
            print(f"   📝 JSON Data: {data}")
            
    except json.JSONDecodeError:
        # Nếu không phải JSON, xử lý text cũ (backward compatible)
        print(f"   ⚠️  Not JSON format, processing as text...")
        
        if message.lower() == "motion":
            motion_count += 1
            last_motion_time = datetime.now()
            print(f"   🚨 PHÁT HIỆN CHUYỂN ĐỘNG!")
            print(f"   📊 Tổng số lần phát hiện: {motion_count}")
            
        elif message.lower() == "no_motion":
            print(f"   ✓ Không có chuyển động")
            
        elif message.lower() == "online":
            print(f"   🟢 ESP32 online")
            
        else:
            print(f"   📝 Message: {message}")
    
    print(f"{'='*60}")

# Callback khi subscribe thành công
def on_subscribe(client, userdata, mid, granted_qos):
    print(f"✓ Subscribe thành công với QoS: {granted_qos[0]}")

# Tạo MQTT client
client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

try:
    print("="*60)
    print("        ESP32 PIR SENSOR - MQTT SUBSCRIBER")
    print("="*60)
    print("🔌 Đang kết nối tới MQTT Broker...")
    print(f"   Broker: {BROKER}:{PORT}")
    print(f"   Client ID: {CLIENT_ID}")
    
    client.connect(BROKER, PORT, 60)
    
    print("\n📡 Đang lắng nghe PIR sensor...")
    print("   🎯 Chờ ESP32 phát hiện chuyển động...")
    print("   ⌨️  Nhấn Ctrl+C để dừng")
    print("="*60)
    
    # Lắng nghe liên tục
    client.loop_forever()
    
except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print("⏹️  DỪNG SUBSCRIBER")
    print(f"📊 Tổng số lần phát hiện chuyển động: {motion_count}")
    if last_motion_time:
        print(f"🕐 Lần cuối phát hiện: {last_motion_time.strftime('%H:%M:%S')}")
    print("="*60)
    client.disconnect()
    print("✓ Đã ngắt kết nối")
    
except Exception as e:
    print(f"\n✗ Lỗi: {e}")
    client.disconnect()
