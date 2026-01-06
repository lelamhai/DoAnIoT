"""
Integration Test Script - Phase 7
Test toàn bộ pipeline: MQTT → Backend → AI → Database → Alert
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
from datetime import datetime
from colorama import init, Fore, Style
import paho.mqtt.client as mqtt

# Initialize colorama
init(autoreset=True)

# Test configuration
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/security/pir/nhom03"
TEST_DURATION = 60  # seconds
TEST_EVENTS = 10


class IntegrationTester:
    """Comprehensive integration testing"""
    
    def __init__(self):
        self.test_results = {
            'mqtt_publish': [],
            'backend_receive': [],
            'ai_prediction': [],
            'database_storage': [],
            'alert_trigger': []
        }
        self.client = None
    
    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}{text.center(70)}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Fore.YELLOW}ℹ️  {text}{Style.RESET_ALL}")
    
    def test_mqtt_connection(self):
        """Test 1: MQTT Connection"""
        self.print_header("TEST 1: MQTT BROKER CONNECTION")
        
        try:
            self.client = mqtt.Client("integration_tester")
            self.client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            self.client.loop_start()
            time.sleep(2)
            
            self.print_success(f"Connected to {MQTT_BROKER}:{MQTT_PORT}")
            self.test_results['mqtt_publish'].append(True)
            return True
            
        except Exception as e:
            self.print_error(f"MQTT connection failed: {e}")
            self.test_results['mqtt_publish'].append(False)
            return False
    
    def test_mqtt_publish(self):
        """Test 2: MQTT Publish Messages"""
        self.print_header("TEST 2: MQTT MESSAGE PUBLISHING")
        
        test_scenarios = [
            {
                "name": "Normal daytime motion",
                "motion": 1,
                "hour": 14,
                "expected": "NORMAL"
            },
            {
                "name": "Suspicious nighttime motion",
                "motion": 1,
                "hour": 2,
                "expected": "SUSPICIOUS"
            },
            {
                "name": "No motion daytime",
                "motion": 0,
                "hour": 10,
                "expected": "NORMAL"
            },
            {
                "name": "No motion nighttime",
                "motion": 0,
                "hour": 3,
                "expected": "NORMAL"
            },
            {
                "name": "High frequency nighttime",
                "motion": 1,
                "hour": 1,
                "expected": "SUSPICIOUS"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            try:
                # Create test event
                timestamp = datetime.now()
                timestamp = timestamp.replace(hour=scenario['hour'])
                
                payload = {
                    "timestamp": timestamp.isoformat(),
                    "motion": scenario["motion"],
                    "sensor_id": f"TEST_{i:03d}",
                    "location": "test_area"
                }
                
                # Publish to MQTT
                result = self.client.publish(
                    MQTT_TOPIC,
                    json.dumps(payload),
                    qos=1
                )
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    self.print_success(
                        f"[{i}/{len(test_scenarios)}] {scenario['name']}: "
                        f"Motion={scenario['motion']}, Hour={scenario['hour']}h "
                        f"(Expected: {scenario['expected']})"
                    )
                    self.test_results['mqtt_publish'].append(True)
                else:
                    self.print_error(f"Failed to publish: {scenario['name']}")
                    self.test_results['mqtt_publish'].append(False)
                
                time.sleep(2)  # Delay giữa các messages
                
            except Exception as e:
                self.print_error(f"Error publishing {scenario['name']}: {e}")
                self.test_results['mqtt_publish'].append(False)
        
        success_rate = sum(self.test_results['mqtt_publish']) / len(self.test_results['mqtt_publish']) * 100
        self.print_info(f"MQTT Publish Success Rate: {success_rate:.1f}%")
    
    def test_database_verification(self):
        """Test 3: Database Storage Verification"""
        self.print_header("TEST 3: DATABASE VERIFICATION")
        
        try:
            from backend.infrastructure.database import Database
            
            db = Database()
            
            # Get recent events
            recent_events = db.get_recent_events(limit=10)
            
            if recent_events:
                self.print_success(f"Retrieved {len(recent_events)} events from database")
                
                # Verify columns
                required_columns = ['timestamp', 'motion', 'sensor_id', 'location', 
                                   'prediction', 'confidence', 'alert_level']
                
                first_event = recent_events[0]
                missing_columns = [col for col in required_columns if col not in first_event]
                
                if not missing_columns:
                    self.print_success("All required columns present")
                    self.test_results['database_storage'].append(True)
                else:
                    self.print_error(f"Missing columns: {missing_columns}")
                    self.test_results['database_storage'].append(False)
                
                # Display sample event
                print(f"\n{Fore.CYAN}Sample Event:{Style.RESET_ALL}")
                for key, value in first_event.items():
                    print(f"  {key}: {value}")
                
            else:
                self.print_error("No events found in database")
                self.test_results['database_storage'].append(False)
            
            db.close()
            
        except Exception as e:
            self.print_error(f"Database verification failed: {e}")
            self.test_results['database_storage'].append(False)
    
    def test_ai_predictions(self):
        """Test 4: AI Prediction Verification"""
        self.print_header("TEST 4: AI PREDICTION VERIFICATION")
        
        try:
            from backend.infrastructure.database import Database
            
            db = Database()
            
            # Get events with predictions
            events = db.get_recent_events(limit=20)
            
            predictions = {
                'NORMAL': 0,
                'SUSPICIOUS': 0,
                'None': 0
            }
            
            alert_levels = {
                'SAFE': 0,
                'WARNING': 0,
                'CRITICAL': 0,
                'None': 0
            }
            
            for event in events:
                pred = event.get('prediction', 'None')
                alert = event.get('alert_level', 'None')
                
                if pred:
                    predictions[pred] = predictions.get(pred, 0) + 1
                if alert:
                    alert_levels[alert] = alert_levels.get(alert, 0) + 1
            
            # Display statistics
            self.print_success(f"Analyzed {len(events)} events")
            
            print(f"\n{Fore.CYAN}Prediction Distribution:{Style.RESET_ALL}")
            for pred, count in predictions.items():
                if count > 0:
                    percentage = count / len(events) * 100
                    print(f"  {pred}: {count} ({percentage:.1f}%)")
            
            print(f"\n{Fore.CYAN}Alert Level Distribution:{Style.RESET_ALL}")
            for level, count in alert_levels.items():
                if count > 0:
                    percentage = count / len(events) * 100
                    icon = {'SAFE': '🟢', 'WARNING': '🟡', 'CRITICAL': '🔴'}.get(level, 'ℹ️')
                    print(f"  {icon} {level}: {count} ({percentage:.1f}%)")
            
            # Verify AI is working
            if predictions.get('NORMAL', 0) > 0 or predictions.get('SUSPICIOUS', 0) > 0:
                self.print_success("AI predictions are being generated")
                self.test_results['ai_prediction'].append(True)
            else:
                self.print_error("No AI predictions found")
                self.test_results['ai_prediction'].append(False)
            
            db.close()
            
        except Exception as e:
            self.print_error(f"AI verification failed: {e}")
            self.test_results['ai_prediction'].append(False)
    
    def test_alert_service(self):
        """Test 5: Alert Service"""
        self.print_header("TEST 5: ALERT SERVICE")
        
        try:
            from backend.services.alert_service import AlertService
            from backend.core.models import MotionEvent, MotionStatus, PredictionResult, PredictionLabel, AlertLevel
            
            # Initialize alert service (console only)
            alert_service = AlertService()
            
            # Test connection
            self.print_info("Testing alert channels...")
            test_results = alert_service.test_connection()
            
            for channel, status in test_results.items():
                if status:
                    self.print_success(f"{channel.upper()} channel: OK")
                else:
                    self.print_error(f"{channel.upper()} channel: FAILED")
            
            # Create test event
            test_event = MotionEvent(
                timestamp=datetime.now(),
                motion=MotionStatus.MOTION_DETECTED,
                sensor_id="INTEGRATION_TEST",
                location="test_area"
            )
            
            test_prediction = PredictionResult(
                timestamp=datetime.now(),
                motion_event=test_event,
                prediction_label=PredictionLabel.SUSPICIOUS,
                confidence=0.95,
                alert_level=AlertLevel.CRITICAL,
                features={'hour': 2, 'is_night': 1, 'frequency_5min': 5, 'duration': 3}
            )
            
            # Send test alert
            self.print_info("Sending test alert...")
            success = alert_service.send_alert(test_event, test_prediction, force=True)
            
            if success:
                self.print_success("Test alert sent successfully")
                self.test_results['alert_trigger'].append(True)
            else:
                self.print_error("Failed to send test alert")
                self.test_results['alert_trigger'].append(False)
            
        except Exception as e:
            self.print_error(f"Alert service test failed: {e}")
            self.test_results['alert_trigger'].append(False)
    
    def test_performance(self):
        """Test 6: Performance Metrics"""
        self.print_header("TEST 6: PERFORMANCE METRICS")
        
        try:
            from backend.infrastructure.database import Database
            
            db = Database()
            
            # Measure query performance
            start_time = time.time()
            events = db.get_recent_events(limit=100)
            query_time = (time.time() - start_time) * 1000  # ms
            
            self.print_success(f"Database query time: {query_time:.2f}ms")
            
            if query_time < 100:
                self.print_success("Query performance: EXCELLENT (<100ms)")
            elif query_time < 500:
                self.print_info("Query performance: GOOD (<500ms)")
            else:
                self.print_error("Query performance: NEEDS OPTIMIZATION (>500ms)")
            
            # Check database size
            db_path = "data/security.db"
            if os.path.exists(db_path):
                db_size = os.path.getsize(db_path) / 1024  # KB
                self.print_info(f"Database size: {db_size:.2f} KB")
            
            db.close()
            
        except Exception as e:
            self.print_error(f"Performance test failed: {e}")
    
    def generate_report(self):
        """Generate final test report"""
        self.print_header("INTEGRATION TEST REPORT")
        
        categories = {
            'MQTT Publishing': self.test_results['mqtt_publish'],
            'Backend Reception': self.test_results['backend_receive'],
            'AI Prediction': self.test_results['ai_prediction'],
            'Database Storage': self.test_results['database_storage'],
            'Alert Service': self.test_results['alert_trigger']
        }
        
        total_tests = 0
        passed_tests = 0
        
        print(f"\n{Fore.CYAN}Test Results Summary:{Style.RESET_ALL}\n")
        
        for category, results in categories.items():
            if results:
                passed = sum(results)
                total = len(results)
                success_rate = passed / total * 100 if total > 0 else 0
                
                total_tests += total
                passed_tests += passed
                
                status_icon = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
                
                print(f"{status_icon} {category}: {passed}/{total} ({success_rate:.1f}%)")
        
        print(f"\n{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        
        overall_success = passed_tests / total_tests * 100 if total_tests > 0 else 0
        
        if overall_success >= 90:
            print(f"{Fore.GREEN}🎉 OVERALL: {passed_tests}/{total_tests} ({overall_success:.1f}%) - EXCELLENT{Style.RESET_ALL}")
        elif overall_success >= 70:
            print(f"{Fore.YELLOW}⚠️  OVERALL: {passed_tests}/{total_tests} ({overall_success:.1f}%) - GOOD{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ OVERALL: {passed_tests}/{total_tests} ({overall_success:.1f}%) - NEEDS IMPROVEMENT{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
    
    def run_all_tests(self):
        """Run complete integration test suite"""
        print(f"\n{Fore.MAGENTA}{'='*70}")
        print(f"{'🧪 IoT SECURITY SYSTEM - INTEGRATION TEST SUITE'.center(70)}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}Test Configuration:{Style.RESET_ALL}")
        print(f"  MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
        print(f"  MQTT Topic: {MQTT_TOPIC}")
        print(f"  Test Events: {TEST_EVENTS}")
        
        try:
            # Run tests
            if self.test_mqtt_connection():
                self.test_mqtt_publish()
                time.sleep(5)  # Wait for backend to process
            
            self.test_database_verification()
            self.test_ai_predictions()
            self.test_alert_service()
            self.test_performance()
            
            # Generate report
            self.generate_report()
            
        except KeyboardInterrupt:
            self.print_error("\nTest interrupted by user")
        
        finally:
            self.cleanup()
            self.print_info("Integration test completed")


if __name__ == "__main__":
    tester = IntegrationTester()
    tester.run_all_tests()
