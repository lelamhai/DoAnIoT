"""
MODULE 2: BACKEND
Nhiệm vụ: Nhận MQTT → Lưu Database
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

if __name__ == "__main__":
    print("=" * 70)
    print("MODULE 2: BACKEND - SIMPLE MODE")
    print("=" * 70)
    print("\nĐang khởi động backend...")
    print("File: backend/simple_main.py")
    print()
    
    # Import and run
    from backend.simple_main import SimpleBackend
    
    backend = SimpleBackend()
    backend.run()
