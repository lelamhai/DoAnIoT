"""
BACKEND - MODULE 1: CHỈ LƯU DỮ LIỆU
Nhiệm vụ: Nhận MQTT messages và lưu vào Database
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.services.mqtt_service import MQTTService
from backend.services.data_processor import DataProcessor
from backend.infrastructure.database import Database
from backend.infrastructure.logger import CSVLogger
from backend.infrastructure.config import ConfigManager
import signal
import time


class SimpleBackend:
    """Backend đơn giản - chỉ lưu dữ liệu"""
    
    def __init__(self):
        print("=" * 60)
        print("BACKEND - SIMPLE MODE")
        print("Nhiệm vụ: Nhận MQTT → Lưu Database")
        print("=" * 60)
        
        # Initialize services
        print("\n[1/4] Khởi tạo Data Processor...")
        self.data_processor = DataProcessor()
        print("     ✓ Done")
        
        print("\n[2/4] Kết nối Database...")
        try:
            config_manager = ConfigManager()
            db_config = config_manager.load_database_config()
            db_path = db_config.path
        except:
            db_path = "data/security.db"
        
        self.database = Database(db_path)
        print(f"     ✓ Database: {db_path}")
        
        print("\n[3/4] Khởi tạo CSV Logger...")
        self.csv_logger = CSVLogger()
        print("     ✓ Done")
        
        print("\n[4/4] Kết nối MQTT...")
        try:
            config_manager = ConfigManager()
            mqtt_config = config_manager.load_mqtt_config()
        except:
            # Default config
            from backend.infrastructure.config import MQTTConfig
            mqtt_config = MQTTConfig(
                broker="broker.hivemq.com",
                port=1883,
                topic="iot/security/pir"
            )
        
        self.mqtt = MQTTService(mqtt_config)
        self.mqtt.connect()
        self.mqtt.subscribe(mqtt_config.topic, self.on_message)
        print(f"     ✓ MQTT: {mqtt_config.broker}:{mqtt_config.port}")
        print(f"     ✓ Topic: {mqtt_config.topic}")
        
        # Statistics
        self.event_count = 0
        self.motion_count = 0
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        print("\n" + "=" * 60)
        print("✓ BACKEND ĐANG CHẠY - CHỜ MQTT MESSAGES...")
        print("=" * 60)
        print("Nhấn Ctrl+C để dừng\n")
    
    def on_message(self, payload):
        """Xử lý MQTT message"""
        try:
            # 1. Validate
            if not self.data_processor.validate_payload(payload):
                print("⚠️ Invalid payload")
                return
            
            # 2. Transform to MotionEvent
            event = self.data_processor.transform_to_event(payload)
            if not event:
                print("⚠️ Failed to transform")
                return
            
            # 3. Update statistics
            self.event_count += 1
            if event.motion.value == 1:
                self.motion_count += 1
            
            # 4. Display
            motion_icon = "🔴" if event.motion.value == 1 else "⚪"
            print(f"[#{self.event_count}] {motion_icon} {event.timestamp.strftime('%H:%M:%S')}")
            print(f"       Motion: {event.motion.value} | Sensor: {event.sensor_id}")
            
            # 5. Save to Database
            self.database.insert_event(event)
            print(f"       ✓ Saved to DB")
            
            # 6. Save to CSV
            self.csv_logger.log_event(event)
            print(f"       ✓ Saved to CSV")
            
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run(self):
        """Run backend"""
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self, signum=None, frame=None):
        """Shutdown gracefully"""
        print("\n\n" + "=" * 60)
        print("ĐANG DỪNG BACKEND...")
        print("=" * 60)
        
        self.running = False
        
        # Disconnect MQTT
        print("  • Ngắt kết nối MQTT...")
        self.mqtt.disconnect()
        
        # Close database
        print("  • Đóng database...")
        self.database.close()
        
        # Statistics
        print(f"\n📊 THỐNG KÊ:")
        print(f"  • Tổng events: {self.event_count}")
        print(f"  • Motion detected: {self.motion_count}")
        
        print("\n✓ Backend đã dừng")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    backend = SimpleBackend()
    backend.run()
