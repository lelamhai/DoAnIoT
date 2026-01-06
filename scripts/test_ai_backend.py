"""
Test AI-enabled backend with sample messages
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime, timedelta

# Config
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "iot/security/pir/nhom03"

# Scenarios để test AI predictions
test_scenarios = [
    {"name": "Morning motion (7h)", "hour": 7, "motion": 1},
    {"name": "Late night motion (2h)", "hour": 2, "motion": 1},  # Should be SUSPICIOUS
    {"name": "Work hours intrusion (14h)", "hour": 14, "motion": 1},  # Should be SUSPICIOUS
    {"name": "Evening activity (20h)", "hour": 20, "motion": 1},  # Normal
    {"name": "No motion", "hour": 10, "motion": 0},  # Normal
]

def publish_test_scenarios():
    """Publish test scenarios"""
    client = mqtt.Client()
    
    print("=" * 70)
    print("TESTING AI-ENABLED BACKEND")
    print("=" * 70)
    print(f"\nConnecting to {BROKER}:{PORT}...")
    
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    
    print(f"Publishing to topic: {TOPIC}\n")
    
    for i, scenario in enumerate(test_scenarios, 1):
        # Create timestamp for the scenario hour
        ts = datetime.now().replace(hour=scenario['hour'], minute=30, second=0, microsecond=0)
        
        payload = {
            "timestamp": ts.isoformat(),
            "motion": scenario['motion'],
            "sensor_id": "TEST_AI",
            "location": "living_room"
        }
        
        print(f"[{i}] {scenario['name']}")
        print(f"    Payload: {json.dumps(payload, indent=2)}")
        
        client.publish(TOPIC, json.dumps(payload))
        print(f"    ✓ Published\n")
        
        time.sleep(2)  # Wait 2s between messages
    
    client.loop_stop()
    client.disconnect()
    
    print("=" * 70)
    print("✅ All test scenarios published!")
    print("=" * 70)
    print("\nCheck backend terminal to see AI predictions:")
    print("  - Morning motion: Should be NORMAL")
    print("  - Late night motion: Should be SUSPICIOUS")
    print("  - Work hours intrusion: Should be SUSPICIOUS")
    print("  - Evening activity: Should be NORMAL")


if __name__ == "__main__":
    publish_test_scenarios()
