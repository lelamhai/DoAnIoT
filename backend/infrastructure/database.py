"""
Database Service - SQLite
Quản lý lưu trữ events vào SQLite database
"""

import sqlite3
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime
from backend.core.models import MotionEvent
from backend.core.enums import MotionStatus


class Database:
    """
    SQLite database service cho IoT Security System
    """
    
    def __init__(self, db_path: str = "data/security.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        
        # Tạo folder data nếu chưa có
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Kết nối đến database"""
        try:
            self.conn = sqlite3.connect(
                str(self.db_path), 
                check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row
            print(f"✓ Database connected: {self.db_path}")
        except Exception as e:
            print(f"✗ Database connection error: {e}")
            raise
    
    def create_tables(self):
        """Tạo tables nếu chưa tồn tại"""
        try:
            # Table: events (lưu trữ motion events)
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    motion INTEGER NOT NULL,
                    sensor_id TEXT,
                    location TEXT,
                    prediction TEXT,
                    confidence REAL,
                    alert_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Index for faster queries
            self.conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON events(timestamp DESC)
            ''')
            
            self.conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_alert_level 
                ON events(alert_level)
            ''')
            
            self.conn.commit()
            print("✓ Database tables initialized")
            
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            raise
    
    def insert_event(
        self, 
        event: MotionEvent,
        prediction: Optional[str] = None,
        confidence: Optional[float] = None,
        alert_level: Optional[str] = None
    ) -> int:
        """
        Insert motion event vào database
        
        Args:
            event: MotionEvent object
            prediction: AI prediction label (NORMAL/SUSPICIOUS)
            confidence: Confidence score (0-1)
            alert_level: Alert level (SAFE/WARNING/CRITICAL)
            
        Returns:
            ID của event đã insert
        """
        try:
            cursor = self.conn.execute('''
                INSERT INTO events (
                    timestamp, motion, sensor_id, location, 
                    prediction, confidence, alert_level
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.timestamp,
                event.motion.value if isinstance(event.motion, MotionStatus) else event.motion,
                event.sensor_id,
                event.location,
                prediction,
                confidence,
                alert_level
            ))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            print(f"✗ Error inserting event: {e}")
            return -1
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """
        Lấy events gần nhất
        
        Args:
            limit: Số lượng events tối đa
            
        Returns:
            List of event dictionaries
        """
        try:
            cursor = self.conn.execute('''
                SELECT * FROM events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"✗ Error getting recent events: {e}")
            return []
    
    def get_events_by_date(self, date: str) -> List[Dict]:
        """
        Lấy events theo ngày
        
        Args:
            date: Date string (YYYY-MM-DD)
            
        Returns:
            List of events for that date
        """
        try:
            cursor = self.conn.execute('''
                SELECT * FROM events 
                WHERE DATE(timestamp) = ?
                ORDER BY timestamp DESC
            ''', (date,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"✗ Error getting events by date: {e}")
            return []
    
    def get_suspicious_events(self, limit: int = 50) -> List[Dict]:
        """
        Lấy các events bất thường (SUSPICIOUS)
        
        Args:
            limit: Số lượng tối đa
            
        Returns:
            List of suspicious events
        """
        try:
            cursor = self.conn.execute('''
                SELECT * FROM events 
                WHERE prediction = 'SUSPICIOUS'
                   OR alert_level IN ('WARNING', 'CRITICAL')
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"✗ Error getting suspicious events: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Lấy thống kê tổng quan
        
        Returns:
            Dictionary với các số liệu thống kê
        """
        try:
            # Total events
            cursor = self.conn.execute('SELECT COUNT(*) as total FROM events')
            total = cursor.fetchone()['total']
            
            # Events hôm nay
            cursor = self.conn.execute('''
                SELECT COUNT(*) as today FROM events 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            today = cursor.fetchone()['today']
            
            # Suspicious events
            cursor = self.conn.execute('''
                SELECT COUNT(*) as suspicious FROM events 
                WHERE prediction = 'SUSPICIOUS'
            ''')
            suspicious = cursor.fetchone()['suspicious']
            
            # Critical alerts
            cursor = self.conn.execute('''
                SELECT COUNT(*) as critical FROM events 
                WHERE alert_level = 'CRITICAL'
            ''')
            critical = cursor.fetchone()['critical']
            
            return {
                'total_events': total,
                'today_events': today,
                'suspicious_count': suspicious,
                'critical_alerts': critical
            }
            
        except Exception as e:
            print(f"✗ Error getting statistics: {e}")
            return {
                'total_events': 0,
                'today_events': 0,
                'suspicious_count': 0,
                'critical_alerts': 0
            }
    
    def delete_old_events(self, days: int = 30):
        """
        Xóa events cũ hơn X ngày (để không bị đầy database)
        
        Args:
            days: Số ngày giữ lại
        """
        try:
            self.conn.execute('''
                DELETE FROM events 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            deleted = self.conn.total_changes
            self.conn.commit()
            
            print(f"✓ Deleted {deleted} old events (>{days} days)")
            
        except Exception as e:
            print(f"✗ Error deleting old events: {e}")
    
    def close(self):
        """Đóng database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")


def test_database():
    """Test database operations"""
    print("=" * 60)
    print("TESTING DATABASE SERVICE")
    print("=" * 60)
    
    # Initialize
    db = Database("data/test_security.db")
    
    # Test insert
    print("\n[Test 1] Inserting events...")
    from datetime import datetime
    
    event1 = MotionEvent(
        timestamp="2026-01-06T20:30:00Z",
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="PIR_TEST_001",
        location="living_room"
    )
    
    id1 = db.insert_event(
        event1, 
        prediction="NORMAL", 
        confidence=0.85,
        alert_level="SAFE"
    )
    print(f"  Inserted event ID: {id1}")
    
    event2 = MotionEvent(
        timestamp="2026-01-06T03:00:00Z",
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="PIR_TEST_001",
        location="living_room"
    )
    
    id2 = db.insert_event(
        event2,
        prediction="SUSPICIOUS",
        confidence=0.95,
        alert_level="CRITICAL"
    )
    print(f"  Inserted event ID: {id2}")
    
    # Test get recent
    print("\n[Test 2] Getting recent events...")
    recent = db.get_recent_events(limit=5)
    print(f"  Found {len(recent)} events")
    for event in recent[:2]:
        print(f"    - {event['timestamp']}: Motion={event['motion']}, Prediction={event['prediction']}")
    
    # Test suspicious events
    print("\n[Test 3] Getting suspicious events...")
    suspicious = db.get_suspicious_events()
    print(f"  Found {len(suspicious)} suspicious events")
    
    # Test statistics
    print("\n[Test 4] Getting statistics...")
    stats = db.get_statistics()
    print(f"  Total events: {stats['total_events']}")
    print(f"  Suspicious: {stats['suspicious_count']}")
    print(f"  Critical alerts: {stats['critical_alerts']}")
    
    # Close
    db.close()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_database()
