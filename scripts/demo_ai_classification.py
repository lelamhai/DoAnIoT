"""
Demo Script - AI Classification
Simulate các scenarios để demo cho khách hàng
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.ai.rule_classifier import RuleBasedClassifier
from backend.core.models import MotionEvent
from datetime import datetime, timedelta
import time


def demo_realtime_classification():
    """Demo real-time classification với manual input"""
    print("\n" + "="*70)
    print("DEMO: AI MOTION CLASSIFICATION SYSTEM")
    print("="*70)
    print("\n📌 Hướng dẫn Demo:")
    print("  1. Nhập giờ (0-23) để simulate chuyển động")
    print("  2. System sẽ classify NORMAL hoặc SUSPICIOUS")
    print("  3. Nhập 'q' để thoát\n")
    
    classifier = RuleBasedClassifier()
    
    # Show current rules
    print("📋 Current Rules:")
    print("  🌙 Đêm khuya (1h-5h) → SUSPICIOUS")
    print("  💼 Giờ làm việc (9h-17h, Thứ 2-6) → SUSPICIOUS")
    print("  🏠 Các giờ khác → NORMAL")
    print("\n" + "-"*70 + "\n")
    
    event_count = 0
    
    while True:
        try:
            # Input giờ
            hour_input = input("Nhập giờ (0-23) hoặc 'q' để thoát: ").strip()
            
            if hour_input.lower() == 'q':
                print("\n👋 Kết thúc demo. Cảm ơn!")
                break
            
            hour = int(hour_input)
            if not (0 <= hour <= 23):
                print("❌ Giờ phải từ 0-23!\n")
                continue
            
            event_count += 1
            
            # Create fake timestamp với giờ đã nhập
            now = datetime.now()
            fake_time = now.replace(hour=hour, minute=0, second=0)
            timestamp = fake_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Create motion event
            event = MotionEvent(
                timestamp=timestamp,
                motion=1,
                sensor_id="DEMO_SENSOR",
                location="living_room"
            )
            
            # Classify
            result = classifier.classify(event)
            
            # Display result
            print("\n" + "="*70)
            print(f"📊 Event #{event_count} - Kết quả phân loại:")
            print("="*70)
            print(f"⏰ Thời gian: {hour:02d}:00")
            print(f"📅 Ngày: {fake_time.strftime('%A, %d/%m/%Y')}")
            print()
            
            # Color-coded output
            if result.alert_level.value == "CRITICAL":
                status_icon = "🚨"
                status_color = "RED"
            elif result.alert_level.value == "WARNING":
                status_icon = "⚠️"
                status_color = "YELLOW"
            else:
                status_icon = "✅"
                status_color = "GREEN"
            
            print(f"{status_icon} Phân loại: {result.label.value}")
            print(f"📈 Độ tin cậy: {result.confidence:.0%}")
            print(f"🎚️  Mức cảnh báo: {result.alert_level.value} ({status_color})")
            print(f"💬 Thông báo: {result.message}")
            print("="*70 + "\n")
            
        except ValueError:
            print("❌ Vui lòng nhập số từ 0-23!\n")
        except KeyboardInterrupt:
            print("\n\n👋 Kết thúc demo. Cảm ơn!")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}\n")


def demo_preset_scenarios():
    """Demo với scenarios định sẵn"""
    print("\n" + "="*70)
    print("DEMO: PRESET SCENARIOS")
    print("="*70 + "\n")
    
    classifier = RuleBasedClassifier()
    
    scenarios = [
        {
            "name": "🏠 Sáng sớm đi làm (7h)",
            "hour": 7,
            "day": 0,  # Monday
            "expected": "NORMAL"
        },
        {
            "name": "🚨 Trộm đột nhập (3h sáng)",
            "hour": 3,
            "day": 2,  # Wednesday
            "expected": "SUSPICIOUS"
        },
        {
            "name": "⚠️ Có người khi đi làm (14h Thứ 3)",
            "hour": 14,
            "day": 1,  # Tuesday
            "expected": "SUSPICIOUS"
        },
        {
            "name": "🏠 Tối về nhà (20h)",
            "hour": 20,
            "day": 3,  # Thursday
            "expected": "NORMAL"
        },
        {
            "name": "🏠 Cuối tuần ở nhà (14h Thứ 7)",
            "hour": 14,
            "day": 5,  # Saturday
            "expected": "NORMAL"
        },
        {
            "name": "🚨 Đêm khuya có chuyển động (2h)",
            "hour": 2,
            "day": 4,  # Friday
            "expected": "SUSPICIOUS"
        }
    ]
    
    print("Đang chạy {} scenarios...\n".format(len(scenarios)))
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}/{len(scenarios)}] {scenario['name']}")
        print("-" * 70)
        
        # Create timestamp
        now = datetime.now()
        fake_time = now.replace(hour=scenario['hour'], minute=0, second=0)
        # Adjust day of week
        days_ahead = scenario['day'] - now.weekday()
        if days_ahead < 0:
            days_ahead += 7
        fake_time = fake_time + timedelta(days=days_ahead)
        timestamp = fake_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        event = MotionEvent(
            timestamp=timestamp,
            motion=1,
            sensor_id="DEMO_SENSOR",
            location="living_room"
        )
        
        result = classifier.classify(event)
        
        # Display
        print(f"  ⏰ Thời gian: {fake_time.strftime('%A %d/%m/%Y, %H:%M')}")
        print(f"  📊 Kết quả: {result.label.value}")
        print(f"  📈 Confidence: {result.confidence:.0%}")
        print(f"  🎚️  Alert: {result.alert_level.value}")
        print(f"  💬 Message: {result.message}")
        
        # Check expected
        is_correct = result.label.value.upper() == scenario['expected']
        status = "✅ ĐÚNG" if is_correct else "❌ SAI"
        print(f"  {status} (Expected: {scenario['expected']})")
        
        time.sleep(0.5)  # Delay cho smooth
    
    print("\n" + "="*70)
    print("✅ Demo hoàn tất!")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n🎬 CHÀO MỪNG ĐẾN VỚI DEMO AI CLASSIFICATION\n")
    print("Chọn chế độ demo:")
    print("  1. Interactive Demo (Nhập giờ thủ công)")
    print("  2. Preset Scenarios (Chạy các kịch bản mẫu)")
    print("  3. Cả hai\n")
    
    choice = input("Chọn (1/2/3): ").strip()
    
    if choice == "1":
        demo_realtime_classification()
    elif choice == "2":
        demo_preset_scenarios()
    elif choice == "3":
        demo_preset_scenarios()
        input("\n⏸️  Nhấn Enter để tiếp tục Interactive Demo...")
        demo_realtime_classification()
    else:
        print("❌ Lựa chọn không hợp lệ!")
