"""
Application Layer - MQTT Service
Quản lý kết nối MQTT, publish/subscribe messages
"""

import paho.mqtt.client as mqtt
import json
import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime
from backend.core.models import MotionEvent
from backend.infrastructure.config import MQTTConfig


class MQTTService:
    """
    MQTT Service sử dụng paho-mqtt client
    Hỗ trợ publish và subscribe với callbacks
    """
    
    def __init__(self, config: MQTTConfig):
        """
        Initialize MQTT Service
        
        Args:
            config: MQTTConfig object với broker settings
        """
        self.config = config
        self.client = mqtt.Client(client_id=config.client_id)
        self.is_connected = False
        self.message_callbacks = []
        
        # Setup callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Setup authentication nếu có
        if config.username and config.password:
            self.client.username_pw_set(config.username, config.password)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        Kết nối tới MQTT Broker
        
        Returns:
            True nếu connect thành công, False nếu fail
        """
        try:
            self.logger.info(f"Connecting to MQTT broker: {self.config.broker}:{self.config.port}")
            self.client.connect(
                self.config.broker, 
                self.config.port, 
                self.config.keep_alive
            )
            self.client.loop_start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối khỏi MQTT Broker"""
        self.logger.info("Disconnecting from MQTT broker")
        self.client.loop_stop()
        self.client.disconnect()
        self.is_connected = False
    
    def subscribe(self, topic: Optional[str] = None, callback: Optional[Callable] = None):
        """
        Subscribe tới MQTT topic
        
        Args:
            topic: Topic để subscribe (mặc định lấy từ config)
            callback: Function được gọi khi nhận message
        """
        if topic is None:
            topic = self.config.topic
        
        self.logger.info(f"Subscribing to topic: {topic}")
        self.client.subscribe(topic, qos=self.config.qos)
        
        if callback:
            self.add_message_callback(callback)
    
    def add_message_callback(self, callback: Callable):
        """
        Thêm callback function để xử lý messages
        
        Args:
            callback: Function nhận payload dict làm tham số
        """
        if callback not in self.message_callbacks:
            self.message_callbacks.append(callback)
    
    def publish(self, payload: Dict[str, Any], topic: Optional[str] = None) -> bool:
        """
        Publish message lên MQTT topic
        
        Args:
            payload: Dictionary data để publish
            topic: Topic để publish (mặc định lấy từ config)
            
        Returns:
            True nếu publish thành công
        """
        if topic is None:
            topic = self.config.topic
        
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=self.config.qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published to {topic}: {message}")
                return True
            else:
                self.logger.error(f"Failed to publish: {result.rc}")
                return False
        except Exception as e:
            self.logger.error(f"Error publishing message: {e}")
            return False
    
    def publish_motion_event(self, event: MotionEvent, topic: Optional[str] = None) -> bool:
        """
        Publish MotionEvent object
        
        Args:
            event: MotionEvent object
            topic: Topic để publish
            
        Returns:
            True nếu publish thành công
        """
        payload = event.to_dict()
        return self.publish(payload, topic)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback khi kết nối thành công"""
        if rc == 0:
            self.is_connected = True
            self.logger.info("Connected to MQTT broker successfully")
        else:
            self.is_connected = False
            self.logger.error(f"Connection failed with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback khi ngắt kết nối"""
        self.is_connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection with code: {rc}")
        else:
            self.logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """
        Callback khi nhận message từ subscribed topic
        """
        try:
            payload = json.loads(msg.payload.decode())
            self.logger.debug(f"Received message from {msg.topic}: {payload}")
            
            # Gọi tất cả callbacks đã register
            for callback in self.message_callbacks:
                try:
                    callback(payload)
                except Exception as e:
                    self.logger.error(f"Error in message callback: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")


class MQTTPublisher(MQTTService):
    """
    MQTT Publisher - chuyên dùng để publish messages
    """
    
    def publish_motion(self, motion: int, sensor_id: str = "PIR_001", 
                      location: str = "living_room") -> bool:
        """
        Publish motion detection event
        
        Args:
            motion: 0 hoặc 1 (no motion / motion detected)
            sensor_id: ID của sensor
            location: Vị trí của sensor
            
        Returns:
            True nếu publish thành công
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "motion": motion,
            "sensor_id": sensor_id,
            "location": location
        }
        return self.publish(payload)


class MQTTSubscriber(MQTTService):
    """
    MQTT Subscriber - chuyên dùng để subscribe và nhận messages
    """
    
    def start_listening(self, topic: Optional[str] = None):
        """
        Bắt đầu lắng nghe messages
        
        Args:
            topic: Topic để subscribe
        """
        if not self.is_connected:
            self.connect()
        
        self.subscribe(topic)
        self.logger.info("Started listening for messages")


if __name__ == "__main__":
    # Test MQTT Service
    from backend.infrastructure.config import ConfigManager
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Load config
    config_manager = ConfigManager()
    mqtt_config = config_manager.load_mqtt_config()
    
    # Test Publisher
    print("=== Testing MQTT Publisher ===")
    publisher = MQTTPublisher(mqtt_config)
    publisher.connect()
    
    import time
    time.sleep(2)  # Wait for connection
    
    # Publish test message
    success = publisher.publish_motion(motion=1, sensor_id="PIR_TEST")
    print(f"Publish result: {success}")
    
    time.sleep(1)
    publisher.disconnect()
