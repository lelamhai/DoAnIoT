"""
Database Setup Script
Initialize SQLite database với schema đầy đủ
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.infrastructure.database import Database
from backend.infrastructure.config import ConfigManager


def setup_database():
    """
    Setup database với schema và indexes
    """
    print("="*60)
    print("DATABASE SETUP")
    print("="*60)
    
    # Load config
    try:
        db_config = ConfigManager.load_database_config()
        db_path = db_config.path
    except:
        db_path = "data/security.db"
        print(f"⚠️ Using default path: {db_path}")
    
    print(f"\n📁 Database path: {db_path}")
    
    # Create database
    db = Database(db_path)
    
    # Create tables
    print("\n🔧 Creating tables...")
    db.create_tables()
    print("✓ Events table created")
    
    # Create indexes for performance
    print("\n📊 Creating indexes...")
    db.conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON events(timestamp DESC)
    ''')
    print("✓ Index on timestamp created")
    
    db.conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_alert_level 
        ON events(alert_level)
    ''')
    print("✓ Index on alert_level created")
    
    db.conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_motion 
        ON events(motion)
    ''')
    print("✓ Index on motion created")
    
    db.conn.commit()
    
    # Verify
    print("\n✅ Verification:")
    cursor = db.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    tables = cursor.fetchall()
    print(f"  Tables: {[t[0] for t in tables]}")
    
    cursor = db.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
    )
    indexes = cursor.fetchall()
    print(f"  Indexes: {[i[0] for i in indexes]}")
    
    # Insert sample data
    print("\n📝 Inserting sample data...")
    from backend.core.models import MotionEvent, MotionStatus
    from datetime import datetime
    
    sample_events = [
        MotionEvent(
            timestamp=datetime.now().isoformat(),
            motion=MotionStatus.NO_MOTION,
            sensor_id="PIR_001",
            location="living_room"
        ),
        MotionEvent(
            timestamp=datetime.now().isoformat(),
            motion=MotionStatus.MOTION_DETECTED,
            sensor_id="PIR_001",
            location="living_room"
        )
    ]
    
    for event in sample_events:
        db.insert_event(event)
    
    print(f"✓ Inserted {len(sample_events)} sample events")
    
    # Show sample data
    print("\n📋 Sample data:")
    recent = db.get_recent_events(limit=5)
    for event in recent:
        print(f"  - {event['timestamp']}: motion={event['motion']}, location={event['location']}")
    
    db.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE SETUP COMPLETED!")
    print("="*60)
    print(f"\n💡 Database ready at: {db_path}")
    print("   You can now run: python backend/main.py\n")


if __name__ == "__main__":
    setup_database()
