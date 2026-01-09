"""SQLite repository for recognition events (name + time only)."""
import sqlite3
from datetime import datetime
from pathlib import Path
from face_app.domain.ports import RecognitionRepoPort
from face_app.config.settings import DB_PATH


class SQLiteRecognitionRepo(RecognitionRepoPort):
    """SQLite adapter for persisting recognition events."""
    
    def __init__(self, db_path: Path = DB_PATH):
        """
        Initialize SQLite repository.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Create table if not exists."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recognitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_event(self, name: str, time: str) -> None:
        """
        Insert a recognition event.
        
        Args:
            name: Person name or "Stranger"
            time: Timestamp in ISO format (YYYY-MM-DD HH:MM:SS)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO recognitions (name, time) VALUES (?, ?)",
            (name, time)
        )
        
        conn.commit()
        conn.close()
    
    def get_last_event_time(self, name: str) -> str | None:
        """
        Get the last time this person was recognized.
        
        Args:
            name: Person name to check
            
        Returns:
            ISO timestamp string or None if never recognized
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT time FROM recognitions WHERE name = ? ORDER BY id DESC LIMIT 1",
            (name,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_all_events(self, limit: int = 100) -> list:
        """
        Get recent recognition events (for debugging/viewing).
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of (id, name, time) tuples
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, name, time FROM recognitions ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        return results
