"""
MQTT Test Subscriber
Script để test subscribe và nhận messages từ MQTT broker
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.config import ConfigManager
from backend.services.mqtt_service import MQTTSubscriber
from backend.services.data_processor import DataProcessor
import logging


class TestMessageHandler:
    """Handler để xử lý messages nhận được"""
    
    def __init__(self):
        self.message_count = 0
        self.motion_detected_count = 0
        self.no_motion_count = 0
        self.data_processor = DataProcessor()
        self.logger = logging.getLogger(__name__)
    
    def handle_message(self, payload: dict):
        """
        Callback function xử lý message
        
        Args:
            payload: Dictionary data từ MQTT message
        """
        self.message_count += 1
        
        # Log raw message
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"📨 Message #{self.message_count} received")
        self.logger.info(f"Raw payload: {payload}")
        
        # Process message
        event = self.data_processor.process_message(payload)
        
        if event:
            # Update counters
            if event.motion.value == 1:
                self.motion_detected_count += 1
                status = "🔴 MOTION DETECTED"
            else:
                self.no_motion_count += 1
                status = "🟢 NO MOTION"
            
            # Log processed event
            self.logger.info(f"Status: {status}")
            self.logger.info(f"Timestamp: {event.timestamp}")
            self.logger.info(f"Sensor ID: {event.sensor_id}")
            self.logger.info(f"Location: {event.location}")
            self.logger.info(f"\n📊 Statistics:")
            self.logger.info(f"   Total messages: {self.message_count}")
            self.logger.info(f"   Motion detected: {self.motion_detected_count}")
            self.logger.info(f"   No motion: {self.no_motion_count}")
        else:
            self.logger.error("❌ Failed to process message")
        
        self.logger.info(f"{'='*60}\n")
    
    def print_summary(self):
        """In tổng kết sau khi stop"""
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"Total messages received: {self.message_count}")
        print(f"Motion detected: {self.motion_detected_count}")
        print(f"No motion: {self.no_motion_count}")
        print("="*60 + "\n")


def main():
    """Main function để test MQTT subscriber"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Load config
    logger.info("Loading MQTT configuration...")
    config_manager = ConfigManager()
    mqtt_config = config_manager.load_mqtt_config()
    
    logger.info(f"MQTT Broker: {mqtt_config.broker}:{mqtt_config.port}")
    logger.info(f"MQTT Topic: {mqtt_config.topic}")
    
    # Create subscriber
    subscriber = MQTTSubscriber(mqtt_config)
    
    # Create message handler
    handler = TestMessageHandler()
    
    # Add callback
    subscriber.add_message_callback(handler.handle_message)
    
    # Connect to broker
    logger.info("Connecting to MQTT broker...")
    if not subscriber.connect():
        logger.error("Failed to connect to MQTT broker")
        return
    
    # Wait for connection
    time.sleep(2)
    
    if not subscriber.is_connected:
        logger.error("Not connected to broker")
        return
    
    logger.info("✅ Connected successfully!")
    
    # Subscribe to topic
    logger.info(f"Subscribing to topic: {mqtt_config.topic}")
    subscriber.subscribe()
    
    logger.info("\n" + "="*60)
    logger.info("🎧 LISTENING FOR MESSAGES...")
    logger.info("="*60)
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
    finally:
        # Print summary
        handler.print_summary()
        
        # Disconnect
        logger.info("Disconnecting from broker...")
        subscriber.disconnect()
        logger.info("Disconnected. Test completed.")


if __name__ == "__main__":
    main()
