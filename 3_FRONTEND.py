"""
MODULE 3: FRONTEND DASHBOARD
Hiển thị dữ liệu từ Database
"""

import subprocess
import sys

if __name__ == "__main__":
    print("=" * 70)
    print("MODULE 3: FRONTEND DASHBOARD - SIMPLE VERSION")
    print("=" * 70)
    print("\nĐang khởi động Streamlit...")
    print("File: frontend/simple_app.py")
    print("\nTruy cập: http://localhost:8501")
    print("=" * 70)
    print()
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/simple_app.py"])
