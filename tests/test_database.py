"""
Unit Tests for Database Operations
Tests SQLite database CRUD operations
"""

import pytest
from datetime import datetime
from backend.infrastructure.database import Database
from backend.core.models import MotionEvent, MotionStatus


class TestDatabase:
    """Test suite for Database class"""
    
    def test_database_initialization(self, database):
        """Test database connection and initialization"""
        assert database.conn is not None
        assert database.db_path is not None
    
    def test_create_tables(self, database):
        """Test table creation"""
        # Check if events table exists
        cursor = database.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'events'
    
    def test_insert_event(self, database, sample_motion_event):
        """Test inserting motion event"""
        database.insert_event(sample_motion_event)
        
        # Verify insertion
        events = database.get_recent_events(limit=1)
        assert len(events) == 1
        assert events[0]['motion'] == 1
        assert events[0]['sensor_id'] == "TEST_SENSOR_001"
    
    def test_insert_event_with_prediction(self, database, sample_motion_event):
        """Test inserting event with AI prediction"""
        database.insert_event(
            sample_motion_event,
            prediction="suspicious",
            alert_level="warning",
            confidence=0.85
        )
        
        events = database.get_recent_events(limit=1)
        assert len(events) == 1
        assert events[0]['prediction'] == "suspicious"
        assert events[0]['alert_level'] == "warning"
        assert events[0]['confidence'] == 0.85
    
    def test_get_recent_events(self, database, sample_motion_event, sample_no_motion_event):
        """Test retrieving recent events"""
        # Insert multiple events
        database.insert_event(sample_motion_event)
        database.insert_event(sample_no_motion_event)
        
        events = database.get_recent_events(limit=2)
        assert len(events) == 2
        
        # Should be ordered by timestamp DESC
        assert events[0]['timestamp'] > events[1]['timestamp']
    
    def test_get_recent_events_limit(self, database, sample_motion_event):
        """Test limit parameter in get_recent_events"""
        # Insert 5 events
        for i in range(5):
            event = MotionEvent(
                timestamp=datetime(2026, 1, 6, 14, i, 0),
                motion=MotionStatus.MOTION_DETECTED,
                sensor_id=f"SENSOR_{i}",
                location="test"
            )
            database.insert_event(event)
        
        # Get only 3
        events = database.get_recent_events(limit=3)
        assert len(events) == 3
    
    def test_get_statistics(self, database, sample_motion_event, sample_no_motion_event):
        """Test statistics retrieval"""
        # Insert test data
        database.insert_event(sample_motion_event, prediction="normal")
        database.insert_event(sample_no_motion_event, prediction="normal")
        
        stats = database.get_statistics()
        
        assert stats['total_events'] >= 2
        assert 'motion_detected' in stats
        assert 'today_events' in stats
    
    def test_database_close(self, test_db_path):
        """Test database connection close"""
        db = Database(test_db_path)
        db.close()
        
        # Connection should be closed
        assert db.conn is None or not db.conn
