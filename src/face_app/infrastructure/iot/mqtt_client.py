"""MQTT client for IoT communication."""
import paho.mqtt.client as mqtt
from typing import Callable, Optional


class MQTTClient:
    """MQTT client wrapper for ESP32 PIR sensor communication."""
    
    def __init__(
        self,
        broker: str = "broker.hivemq.com",
        port: int = 1883,
        client_id: str = "face_recognition_app",
        keepalive: int = 60
    ):
        """
        Initialize MQTT client.
        
        Args:
            broker: MQTT broker address
            port: MQTT broker port
            client_id: Client identifier
            keepalive: Keepalive interval in seconds
        """
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        
        # Create MQTT client
        self.client = mqtt.Client(client_id=client_id)
        
        # Callback storage
        self._topic_callbacks = {}
        
        # Connection status
        self._connected = False
        
        # Setup callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker."""
        if rc == 0:
            self._connected = True
            print(f"   ✅ MQTT connected successfully (rc={rc})")
            
            # Resubscribe to all topics
            for topic in self._topic_callbacks.keys():
                client.subscribe(topic)
                print(f"   📶 Subscribed to: {topic}")
        else:
            self._connected = False
            print(f"   ❌ MQTT connection failed (rc={rc})")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker."""
        self._connected = False
        if rc != 0:
            print(f"   ⚠️  Unexpected MQTT disconnect (rc={rc})")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received."""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        # Call registered callback for this topic
        if topic in self._topic_callbacks:
            callback = self._topic_callbacks[topic]
            callback(payload)
    
    def subscribe(self, topic: str, callback: Callable[[str], None]) -> None:
        """
        Subscribe to MQTT topic with callback.
        
        Args:
            topic: MQTT topic to subscribe
            callback: Function to call when message received (receives payload string)
        """
        self._topic_callbacks[topic] = callback
        
        # If already connected, subscribe immediately
        if self._connected:
            self.client.subscribe(topic)
    
    def connect(self, timeout: int = 3) -> bool:
        """
        Connect to MQTT broker (non-blocking).
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection initiated successfully
        """
        try:
            # Use connect_async for non-blocking connection
            self.client.connect_async(self.broker, self.port, self.keepalive)
            
            # Start network loop in background thread
            self.client.loop_start()
            
            print(f"   📡 Connecting to MQTT broker: {self.broker}:{self.port}")
            return True
            
        except Exception as e:
            print(f"   ❌ MQTT connect error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        if self._connected or self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                print("   👋 MQTT disconnected")
            except:
                pass
    
    def is_connected(self) -> bool:
        """Check if connected to broker."""
        return self._connected
