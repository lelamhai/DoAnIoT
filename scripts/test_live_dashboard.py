"""
Phase 6 Test Script
Test dashboard với live backend và real-time updates
"""

import sys
from pathlib import Path
import time
from datetime import datetime
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.database import Database

def simulate_live_events():
    """Simulate live events being added to database"""
    print("=" * 70)
    print("SIMULATING LIVE EVENTS FOR DASHBOARD")
    print("=" * 70)
    print("\nThis will add events every 5 seconds.")
    print("Watch the dashboard auto-refresh to see real-time updates!")
    print("\nPress Ctrl+C to stop\n")
    
    db = Database("data/security.db")
    
    try:
        event_count = 0
        while True:
            # Random motion
            motion = random.choice([0, 1])
            hour = datetime.now().hour
            
            # Determine prediction based on hour
            if 6 <= hour <= 9 or 18 <= hour <= 23:
                # Normal hours
                prediction = 'normal'
                alert_level = 'safe'
                confidence = random.uniform(0.85, 0.99)
            elif 1 <= hour <= 5:
                # Suspicious at night
                if motion == 1:
                    prediction = 'suspicious'
                    alert_level = 'critical'
                    confidence = random.uniform(0.7, 0.95)
                else:
                    prediction = 'normal'
                    alert_level = 'safe'
                    confidence = random.uniform(0.9, 0.99)
            else:
                # Work hours
                if motion == 1:
                    prediction = 'suspicious'
                    alert_level = 'warning'
                    confidence = random.uniform(0.6, 0.85)
                else:
                    prediction = 'normal'
                    alert_level = 'safe'
                    confidence = random.uniform(0.85, 0.99)
            
            # Insert directly to database
            timestamp = datetime.now().isoformat()
            db.conn.execute('''
                INSERT INTO events (timestamp, motion, sensor_id, location, prediction, confidence, alert_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, motion, "LIVE_SENSOR", "living_room", prediction, confidence, alert_level))
            db.conn.commit()
            
            event_count += 1
            
            # Display
            motion_icon = "🔴" if motion == 1 else "🟢"
            alert_icon = {"safe": "✅", "warning": "⚠️", "critical": "🚨"}.get(alert_level, "❓")
            
            print(f"[Event #{event_count}] {motion_icon} {alert_icon} | Motion: {motion} | "
                  f"Prediction: {prediction.upper()} ({confidence:.1%}) | Alert: {alert_level.upper()}")
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print(f"\n\n⏸️ Stopped after {event_count} events")
        db.close()
        print("✅ Database closed")


if __name__ == "__main__":
    print("\n📊 Make sure dashboard is running:")
    print("   streamlit run frontend/app.py")
    print("\nStarting in 3 seconds...\n")
    time.sleep(3)
    simulate_live_events()
