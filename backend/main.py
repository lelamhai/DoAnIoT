"""
Backend Main Entry Point
Tích hợp MQTT Subscriber + Database + CSV Logging + AI Classification + Alerts + Monitoring
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.services.mqtt_service import MQTTService
from backend.services.data_processor import DataProcessor
from backend.services.ai_service import AIService
from backend.services.alert_service import AlertService
from backend.infrastructure.database import Database
from backend.infrastructure.logger import CSVLogger
from backend.infrastructure.system_monitor import SystemMonitor
from backend.infrastructure.config import ConfigManager, MQTTConfig
from backend.core.models import MotionEvent
from datetime import datetime
import signal
import time
import threading
from pathlib import Path


class IoTBackend:
    """
    Main backend application
    Nhận MQTT messages → Process → Save to Database & CSV
    """
    
    def __init__(self):
        print("="*70)
        print("IoT SECURITY MONITORING SYSTEM - BACKEND")
        print("="*70)
        
        # Load configurations
        print("\nLoading configurations...")
        try:
            config_manager = ConfigManager()
            self.mqtt_config = config_manager.load_mqtt_config()
            print(f"  ✓ MQTT Config: {self.mqtt_config.broker}:{self.mqtt_config.port}")
        except Exception as e:
            print(f"  ⚠️ MQTT config error: {e}, using defaults")
            self.mqtt_config = None
        
        try:
            config_manager = ConfigManager()
            self.db_config = config_manager.load_database_config()
            print(f"  ✓ Database Config: {self.db_config.path}")
        except Exception as e:
            print(f"  ⚠️ Database config error: {e}, using defaults")
            self.db_config = None
        
        # Initialize services
        print("\nInitializing services...")
        
        self.data_processor = DataProcessor()
        print("  ✓ Data Processor initialized")
        
        # Database
        db_path = self.db_config.path if self.db_config else "data/security.db"
        self.database = Database(db_path)
        print(f"  ✓ Database connected: {db_path}")
        
        # CSV Logger
        self.csv_logger = CSVLogger()
        print("  ✓ CSV Logger initialized")
        
        # AI Service
        try:
            model_path = Path("ai_model/models/classifier.pkl")
            if model_path.exists():
                self.ai_service = AIService()
                print("  ✓ AI Service initialized")
                self.ai_enabled = True
            else:
                print("  ⚠️ AI model not found - running without AI")
                self.ai_service = None
                self.ai_enabled = False
        except Exception as e:
            print(f"  ⚠️ AI initialization failed: {e}")
            self.ai_service = None
            self.ai_enabled = False
        
        # Alert Service
        try:
            self.alert_service = AlertService()
            print("  ✓ Alert Service initialized")
            self.alert_enabled = True
        except Exception as e:
            print(f"  ⚠️ Alert Service initialization failed: {e}")
            self.alert_service = None
            self.alert_enabled = False
        
        # System Monitor
        self.system_monitor = SystemMonitor()
        print("  ✓ System Monitor initialized")
        
        # MQTT Service
        if not self.mqtt_config:
            # Create default config if not loaded
            self.mqtt_config = MQTTConfig(
                broker="test.mosquitto.org",
                port=1883,
                topic="iot/security/pir/nhom03",
                client_id="backend_subscriber_nhom03",
                qos=1
            )
        
        self.mqtt_subscriber = MQTTService(self.mqtt_config)
        print(f"  ✓ MQTT Service created")
        print(f"    Broker: {self.mqtt_config.broker}:{self.mqtt_config.port}")
        print(f"    Topic: {self.mqtt_config.topic}")
        
        # Statistics
        self.event_count = 0
        self.motion_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        # Monitoring thread
        self.monitoring_thread = None
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n\n⏸️ Shutdown signal received...")
        self.stop()
    
    def _on_message_received(self, payload: dict):
        """
        Callback khi nhận MQTT message
        
        Args:
            payload: JSON payload từ MQTT
        """
        try:
            # Validate payload
            if not self.data_processor.validate_payload(payload):
                print(f"⚠️ Invalid payload: {payload}")
                self.error_count += 1
                self.csv_logger.log_error(f"Invalid payload: {payload}")
                return
            
            # Transform to MotionEvent
            event = self.data_processor.transform_to_event(payload)
            if not event:
                print(f"⚠️ Failed to transform payload: {payload}")
                self.error_count += 1
                return
            
            # Update statistics
            self.event_count += 1
            if event.motion.value == 1:
                self.motion_count += 1
            
            # AI Prediction
            prediction = None
            prediction_label = "unknown"
            confidence = 0.0
            alert_level = "safe"
            
            if self.ai_enabled and self.ai_service:
                try:
                    # Get recent events for context
                    recent_events = self.database.get_recent_events(limit=10)
                    history = [MotionEvent.from_dict(e) for e in recent_events]
                    
                    # Predict
                    prediction = self.ai_service.predict(event, history)
                    prediction_label = prediction.prediction_label.value
                    confidence = prediction.confidence
                    alert_level = prediction.alert_level.value
                except Exception as e:
                    print(f"  ⚠️ AI prediction error: {e}")
            
            # Display event
            motion_icon = "🔴" if event.motion.value == 1 else "🟢"
            ai_icon = "" if not prediction else ("⚠️" if prediction.is_abnormal else "✅")
            print(f"\n[Event #{self.event_count}] {motion_icon} {ai_icon} {event.timestamp}")
            print(f"  Motion: {event.motion.value} | Sensor: {event.sensor_id} | Location: {event.location}")
            
            if prediction:
                print(f"  AI: {prediction_label.upper()} ({confidence:.1%}) | Alert: {alert_level.upper()}")
            
            # Save to database (with AI predictions)
            try:
                self.database.insert_event(
                    event, 
                    prediction=prediction_label,
                    alert_level=alert_level,
                    confidence=confidence
                )
                print(f"  ✓ Saved to database")
            except Exception as e:
                print(f"  ✗ Database error: {e}")
                self.csv_logger.log_error(f"Database insert failed: {e}")
            
            # Send alert if necessary
            if self.alert_enabled and self.alert_service and prediction:
                try:
                    alert_sent = self.alert_service.send_alert(event, prediction)
                    if alert_sent:
                        print(f"  🔔 Alert sent: {alert_level.upper()}")
                except Exception as e:
                    print(f"  ⚠️ Alert error: {e}")
            
            # Save to CSV (with AI predictions)
            try:
                self.csv_logger.log_event(
                    event,
                    prediction=prediction_label,
                    alert_level=alert_level,
                    confidence=confidence
                )
                print(f"  ✓ Logged to CSV")
            except Exception as e:
                print(f"  ✗ CSV logging error: {e}")
            
            # Show statistics every 10 events
            if self.event_count % 10 == 0:
                self._show_statistics()
        
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            self.error_count += 1
            self.csv_logger.log_error(f"Message processing error: {e}")
    
    def _monitor_system(self):
        """Background monitoring thread"""
        while self.running:
            self.system_monitor.log_metrics()
            time.sleep(30)  # Log every 30 seconds
    
    def _show_statistics(self):
        """Display current statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        print(f"\n📊 Statistics:")
        print(f"  Total Events: {self.event_count}")
        print(f"  Motion Detected: {self.motion_count}")
        print(f"  Errors: {self.error_count}")
        print(f"  Uptime: {uptime:.0f}s")
        print(f"  Events/min: {self.event_count/(uptime/60):.1f}" if uptime > 0 else "  Events/min: N/A")
    
    def start(self):
        """Start backend service"""
        print("\n" + "="*70)
        print("▶️ STARTING BACKEND SERVICE")
        print("="*70)
        
        # Connect MQTT
        print("\n📡 Connecting to MQTT broker...")
        self.mqtt_subscriber.connect()
        
        # Subscribe with callback
        print(f"📥 Subscribing to topic: {self.mqtt_config.topic}")
        self.mqtt_subscriber.subscribe(callback=self._on_message_received)
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitoring_thread.start()
        print("  ✓ System monitoring started")
        
        print("\n✅ Backend is running!")
        print("   Waiting for MQTT messages...")
        print("   Press Ctrl+C to stop")
        print("   Type 'health' + Enter to check system health\n")
        
        self.running = True
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
                
                # Check for health command (optional)
                # Note: This is basic, could be improved with async input
                
        except KeyboardInterrupt:
            print("\n⏸️ Keyboard interrupt received")
            self.stop()
    
    def stop(self):
        """Stop backend service gracefully"""
        print("\n🛑 Stopping backend service...")
        
        self.running = False
        
        # Show final statistics
        print("\n📊 Final Statistics:")
        self._show_statistics()
        
        # Show system health
        print("\n🔍 Final System Health:")
        self.system_monitor.print_status()
        
        # Disconnect MQTT
        if self.mqtt_subscriber:
            self.mqtt_subscriber.disconnect()
            print("  ✓ MQTT disconnected")
        
        # Close database
        if self.database:
            self.database.close()
            print("  ✓ Database closed")
        
        print("\n✅ Backend stopped successfully")
        print("="*70)


def main():
    """Main entry point"""
    backend = IoTBackend()
    backend.start()


if __name__ == "__main__":
    main()
