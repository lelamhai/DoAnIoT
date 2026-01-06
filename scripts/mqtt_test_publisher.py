"""
MQTT Test Publisher
Script để test publish messages lên MQTT broker
"""

import sys
import time
import random
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.config import ConfigManager
from backend.services.mqtt_service import MQTTPublisher
import logging


def main():
    """Main function để test MQTT publisher"""
    
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
    
    # Create publisher
    publisher = MQTTPublisher(mqtt_config)
    
    # Connect to broker
    logger.info("Connecting to MQTT broker...")
    if not publisher.connect():
        logger.error("Failed to connect to MQTT broker")
        return
    
    # Wait for connection
    time.sleep(2)
    
    if not publisher.is_connected:
        logger.error("Not connected to broker")
        return
    
    logger.info("✅ Connected successfully!")
    
    try:
        # Publish test messages
        logger.info("\n=== Publishing Test Messages ===")
        
        # Test 1: Motion detected
        logger.info("\n1. Publishing MOTION DETECTED...")
        success = publisher.publish_motion(
            motion=1,
            sensor_id="PIR_001",
            location="living_room"
        )
        logger.info(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        time.sleep(1)
        
        # Test 2: No motion
        logger.info("\n2. Publishing NO MOTION...")
        success = publisher.publish_motion(
            motion=0,
            sensor_id="PIR_001",
            location="living_room"
        )
        logger.info(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        time.sleep(1)
        
        # Test 3: Simulate random motion pattern
        logger.info("\n3. Simulating random motion pattern (10 messages)...")
        for i in range(10):
            motion = random.choice([0, 1])
            success = publisher.publish_motion(
                motion=motion,
                sensor_id="PIR_001",
                location="living_room"
            )
            status = "MOTION" if motion == 1 else "NO_MOTION"
            logger.info(f"   [{i+1}/10] {status}: {'✅' if success else '❌'}")
            time.sleep(0.5)
        
        logger.info("\n✅ All test messages published successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Error during publishing: {e}")
    finally:
        # Disconnect
        logger.info("\nDisconnecting from broker...")
        publisher.disconnect()
        logger.info("Disconnected. Test completed.")


def continuous_publish():
    """
    Continuous publishing mode - publish random motion every 2 seconds
    Hữu ích cho testing real-time dashboard
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Load config
    config_manager = ConfigManager()
    mqtt_config = config_manager.load_mqtt_config()
    
    # Create publisher
    publisher = MQTTPublisher(mqtt_config)
    publisher.connect()
    time.sleep(2)
    
    if not publisher.is_connected:
        logger.error("Failed to connect")
        return
    
    logger.info("🚀 Continuous publishing mode started")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        count = 0
        while True:
            motion = random.choice([0, 0, 0, 1])  # 75% no motion, 25% motion
            success = publisher.publish_motion(motion=motion)
            
            status = "🔴 MOTION" if motion == 1 else "🟢 NO_MOTION"
            logger.info(f"[{count:04d}] {status} - {'✅' if success else '❌'}")
            
            count += 1
            time.sleep(2)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️  Stopped by user")
    finally:
        publisher.disconnect()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='MQTT Test Publisher')
    parser.add_argument(
        '--continuous', 
        action='store_true',
        help='Run in continuous publishing mode'
    )
    
    args = parser.parse_args()
    
    if args.continuous:
        continuous_publish()
    else:
        main()
