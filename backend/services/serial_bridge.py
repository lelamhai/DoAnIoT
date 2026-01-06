"""
Application Layer - Serial to MQTT Bridge
Đọc dữ liệu từ Arduino qua Serial Port và publish lên MQTT Broker
"""

import serial
import json
import logging
import time
import re
from datetime import datetime
from typing import Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.config import ConfigManager
from backend.services.mqtt_service import MQTTPublisher


class SerialBridge:
    """
    Serial to MQTT Bridge
    Đọc JSON messages từ Arduino Serial và publish lên MQTT
    """
    
    def __init__(self, port: str, baud_rate: int = 115200):
        """
        Initialize Serial Bridge
        
        Args:
            port: COM port (e.g., "COM3" on Windows, "/dev/ttyUSB0" on Linux)
            baud_rate: Baud rate (default: 115200)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.mqtt_publisher = None
        self.logger = logging.getLogger(__name__)
        self.message_count = 0
        
    def connect_serial(self) -> bool:
        """Kết nối tới Serial Port"""
        try:
            self.logger.info(f"Connecting to serial port: {self.port}")
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1
            )
            time.sleep(2)  # Wait for Arduino to reset
            self.logger.info(f"✓ Serial connected: {self.port} @ {self.baud_rate}")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to serial port: {e}")
            return False
    
    def setup_mqtt(self) -> bool:
        """Setup MQTT Publisher"""
        try:
            config_manager = ConfigManager()
            mqtt_config = config_manager.load_mqtt_config()
            
            self.mqtt_publisher = MQTTPublisher(mqtt_config)
            if self.mqtt_publisher.connect():
                time.sleep(2)
                return self.mqtt_publisher.is_connected
            return False
        except Exception as e:
            self.logger.error(f"Failed to setup MQTT: {e}")
            return False
    
    def parse_serial_line(self, line: str) -> Optional[dict]:
        """
        Parse một dòng từ Serial
        
        Args:
            line: Dòng text từ Serial
            
        Returns:
            Dictionary payload hoặc None nếu parse fail
        """
        line = line.strip()
        
        # Skip empty lines và log messages
        if not line or not line.startswith('{'):
            return None
        
        try:
            # Try parse as JSON
            payload = json.loads(line)
            
            # Replace uptime timestamp with real timestamp
            if 'timestamp' in payload and payload['timestamp'].startswith('UPTIME_'):
                payload['timestamp'] = datetime.now().isoformat()
            
            return payload
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON: {line[:50]}... Error: {e}")
            return None
    
    def process_message(self, payload: dict) -> bool:
        """
        Process và publish message
        
        Args:
            payload: Dictionary data
            
        Returns:
            True nếu publish thành công
        """
        # Validate payload
        if 'motion' not in payload:
            self.logger.warning(f"Invalid payload (missing 'motion'): {payload}")
            return False
        
        # Publish to MQTT
        if self.mqtt_publisher and self.mqtt_publisher.is_connected:
            success = self.mqtt_publisher.publish(payload)
            
            if success:
                self.message_count += 1
                motion_status = "MOTION" if payload['motion'] == 1 else "NO_MOTION"
                self.logger.info(f"[{self.message_count}] {motion_status} → MQTT")
            
            return success
        else:
            self.logger.error("MQTT not connected")
            return False
    
    def run(self):
        """
        Main loop - đọc Serial và publish MQTT
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("Serial to MQTT Bridge Started")
        self.logger.info("="*60)
        
        # Connect Serial
        if not self.connect_serial():
            self.logger.error("Cannot start without serial connection")
            return
        
        # Setup MQTT
        if not self.setup_mqtt():
            self.logger.error("Cannot start without MQTT connection")
            return
        
        self.logger.info("\n✓ Bridge ready! Listening for messages...")
        self.logger.info("Press Ctrl+C to stop\n")
        
        try:
            while True:
                if self.serial.in_waiting > 0:
                    try:
                        # Read line from serial
                        line = self.serial.readline().decode('utf-8', errors='ignore')
                        
                        # Parse payload
                        payload = self.parse_serial_line(line)
                        
                        if payload:
                            # Process and publish
                            self.process_message(payload)
                        elif line.strip() and not line.strip().startswith('='):
                            # Print non-JSON lines (debug logs from Arduino)
                            self.logger.debug(f"Arduino: {line.strip()}")
                    
                    except Exception as e:
                        self.logger.error(f"Error processing line: {e}")
                
                time.sleep(0.01)  # Small delay
                
        except KeyboardInterrupt:
            self.logger.info("\n⚠️  Interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("\nCleaning up...")
        
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("✓ Serial port closed")
        
        if self.mqtt_publisher:
            self.mqtt_publisher.disconnect()
            self.logger.info("✓ MQTT disconnected")
        
        self.logger.info(f"Total messages processed: {self.message_count}")
        self.logger.info("Bridge stopped.")


def list_serial_ports():
    """List available serial ports"""
    import serial.tools.list_ports
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No serial ports found")
        return []
    
    print("\nAvailable Serial Ports:")
    print("-" * 50)
    for i, port in enumerate(ports):
        print(f"{i+1}. {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Hardware ID: {port.hwid}")
        print()
    
    return [port.device for port in ports]


def main():
    """Main function"""
    import argparse
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Serial to MQTT Bridge')
    parser.add_argument(
        '--port',
        type=str,
        help='Serial port (e.g., COM3 or /dev/ttyUSB0)'
    )
    parser.add_argument(
        '--baud',
        type=int,
        default=115200,
        help='Baud rate (default: 115200)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available serial ports'
    )
    
    args = parser.parse_args()
    
    # List ports nếu được yêu cầu
    if args.list:
        list_serial_ports()
        return
    
    # Determine port
    port = args.port
    if not port:
        # Auto-detect first available port
        ports = list_serial_ports()
        if ports:
            port = ports[0]
            print(f"\nAuto-selected port: {port}\n")
        else:
            print("No serial ports found. Please specify --port")
            return
    
    # Create and run bridge
    bridge = SerialBridge(port=port, baud_rate=args.baud)
    bridge.run()


if __name__ == "__main__":
    main()
