"""
Script xóa toàn bộ dữ liệu trong database
"""
import sqlite3
import os

db_path = "data/security.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Xóa tất cả records
    cursor.execute("DELETE FROM events")
    conn.commit()
    
    # Đếm số records còn lại
    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✓ Đã xóa toàn bộ dữ liệu!")
    print(f"  Records còn lại: {count}")
else:
    print("⚠️ Database không tồn tại")
