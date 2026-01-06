"""
Demo Dashboard Script
Populate database với sample data để demo dashboard
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.infrastructure.database import Database
from backend.core.models import MotionEvent
from backend.core.enums import MotionStatus

def generate_demo_data():
    """Generate realistic demo data for dashboard"""
    print("=" * 70)
    print("GENERATING DEMO DATA FOR DASHBOARD")
    print("=" * 70)
    
    db = Database("data/security.db")
    
    # Clear existing data (optional)
    print("\n⚠️  Clearing existing events...")
    db.conn.execute("DELETE FROM events")
    db.conn.commit()
    
    # Generate events for last 24 hours
    print("\n📊 Generating 24 hours of realistic data...")
    
    now = datetime.now()
    events_generated = 0
    
    # Generate events every 5 minutes for 24 hours
    for i in range(288):  # 24h * 60min / 5min
        timestamp = now - timedelta(minutes=i*5)
        hour = timestamp.hour
        
        # Realistic patterns
        # Morning (6-9h): High activity
        if 6 <= hour <= 9:
            motion = random.choices([0, 1], weights=[0.2, 0.8])[0]
            prediction = 'normal'
            alert_level = 'safe'
            confidence = random.uniform(0.85, 0.99)
        
        # Work hours (9-17h): Low activity
        elif 9 <= hour <= 17:
            motion = random.choices([0, 1], weights=[0.95, 0.05])[0]
            if motion == 1:
                # Suspicious during work hours
                prediction = 'suspicious'
                alert_level = random.choice(['warning', 'critical'])
                confidence = random.uniform(0.6, 0.85)
            else:
                prediction = 'normal'
                alert_level = 'safe'
                confidence = random.uniform(0.85, 0.99)
        
        # Evening (18-23h): High activity
        elif 18 <= hour <= 23:
            motion = random.choices([0, 1], weights=[0.3, 0.7])[0]
            prediction = 'normal'
            alert_level = 'safe'
            confidence = random.uniform(0.85, 0.99)
        
        # Late night (0-5h): Very low activity, suspicious if detected
        else:
            motion = random.choices([0, 1], weights=[0.95, 0.05])[0]
            if motion == 1:
                # Suspicious at night
                prediction = 'suspicious'
                alert_level = 'critical'
                confidence = random.uniform(0.7, 0.95)
            else:
                prediction = 'normal'
                alert_level = 'safe'
                confidence = random.uniform(0.9, 0.99)
        
        # Create event
        event = MotionEvent(
            timestamp=timestamp.isoformat(),
            motion=MotionStatus(motion),
            sensor_id="PIR_DEMO_01",
            location="living_room"
        )
        
        # Insert to database
        db.insert_event(
            event,
            prediction=prediction,
            alert_level=alert_level,
            confidence=confidence
        )
        
        events_generated += 1
        
        # Progress
        if events_generated % 50 == 0:
            print(f"  Generated {events_generated} events...")
    
    print(f"\n✅ Generated {events_generated} events")
    
    # Show statistics
    try:
        stats = db.get_statistics()
        print("\n📊 Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"\n⚠️ Could not fetch statistics: {e}")
        # Manual count
        events = db.get_recent_events(limit=10000)
        motion_count = sum(1 for e in events if e.get('motion') == 1)
        print(f"\n📊 Statistics:")
        print(f"  Total Events: {len(events)}")
        print(f"  Motion Detected: {motion_count}")
    
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ DEMO DATA GENERATION COMPLETED!")
    print("=" * 70)
    print("\nNow run the dashboard:")
    print("  streamlit run frontend/app.py")


if __name__ == "__main__":
    generate_demo_data()
