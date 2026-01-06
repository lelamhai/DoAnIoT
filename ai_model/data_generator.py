"""
AI Model - Data Generator
Tạo synthetic dataset để train model phân loại Normal/Suspicious
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path


def generate_training_data(n_samples: int = 500, output_path: str = "ai_model/datasets/training_data.csv"):
    """
    Generate synthetic training data dựa trên patterns thực tế
    
    Args:
        n_samples: Số lượng samples cần tạo
        output_path: Path để lưu CSV
    
    Returns:
        DataFrame với training data
    """
    print(f"Generating {n_samples} training samples...")
    
    data = []
    start_date = datetime(2026, 1, 1, 0, 0, 0)
    
    for i in range(n_samples):
        # Random timestamp trong 30 ngày
        days_offset = np.random.randint(0, 30)
        hour = np.random.randint(0, 24)
        minute = np.random.randint(0, 60)
        
        timestamp = start_date + timedelta(days=days_offset, hours=hour, minutes=minute)
        day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
        
        # Tạo patterns realistic
        
        # NORMAL PATTERNS
        # 1. Sáng (6h-9h) - đi làm
        if 6 <= hour <= 9:
            motion = np.random.choice([0, 1], p=[0.2, 0.8])  # 80% có chuyển động
            label = 0  # Normal
            frequency = np.random.randint(10, 25)  # Tần suất cao
            duration = np.random.uniform(2, 8)  # 2-8 giây
        
        # 2. Tối (18h-23h) - sinh hoạt
        elif 18 <= hour <= 23:
            motion = np.random.choice([0, 1], p=[0.3, 0.7])  # 70% có chuyển động
            label = 0  # Normal
            frequency = np.random.randint(15, 35)
            duration = np.random.uniform(3, 12)
        
        # 3. Cuối tuần ban ngày (8h-22h)
        elif day_of_week >= 5 and 8 <= hour <= 22:
            motion = np.random.choice([0, 1], p=[0.25, 0.75])  # 75% có chuyển động
            label = 0  # Normal
            frequency = np.random.randint(20, 45)
            duration = np.random.uniform(5, 20)
        
        # 4. Giờ làm việc (9h-17h) ngày thường - ít chuyển động
        elif day_of_week < 5 and 9 <= hour <= 17:
            motion = np.random.choice([0, 1], p=[0.95, 0.05])  # 95% không có
            if motion == 1:
                label = 1  # SUSPICIOUS - có người khi đang đi làm
                frequency = np.random.randint(5, 15)
                duration = np.random.uniform(10, 60)
            else:
                label = 0  # Normal
                frequency = 0
                duration = 0
        
        # SUSPICIOUS PATTERNS
        # 5. Đêm khuya (1h-5h)
        elif 1 <= hour <= 5:
            motion = np.random.choice([0, 1], p=[0.9, 0.1])  # 90% không có
            if motion == 1:
                label = 1  # SUSPICIOUS - chuyển động đêm khuya
                frequency = np.random.randint(3, 12)
                duration = np.random.uniform(15, 90)  # Lâu hơn bình thường
            else:
                label = 0  # Normal
                frequency = 0
                duration = 0
        
        # 6. Nửa đêm (23h-1h)
        elif hour == 23 or hour == 0:
            motion = np.random.choice([0, 1], p=[0.7, 0.3])
            if motion == 1:
                # 50% suspicious, 50% normal (có thể ngủ muộn)
                label = np.random.choice([0, 1], p=[0.5, 0.5])
                frequency = np.random.randint(5, 20)
                duration = np.random.uniform(3, 15)
            else:
                label = 0
                frequency = 0
                duration = 0
        
        # Default
        else:
            motion = np.random.choice([0, 1], p=[0.6, 0.4])
            label = 0
            frequency = np.random.randint(5, 20)
            duration = np.random.uniform(2, 10)
        
        # Add noise - realistic imperfections
        if np.random.random() < 0.05:  # 5% noise
            label = 1 - label  # Flip label
        
        data.append({
            'timestamp': timestamp.isoformat(),
            'motion': motion,
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': 1 if day_of_week >= 5 else 0,
            'is_night': 1 if (hour >= 22 or hour <= 6) else 0,
            'frequency_5min': frequency,
            'duration': duration,
            'label': label  # 0=Normal, 1=Suspicious
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Generated {len(df)} samples")
    print(f"   Normal: {(df['label']==0).sum()} ({(df['label']==0).sum()/len(df)*100:.1f}%)")
    print(f"   Suspicious: {(df['label']==1).sum()} ({(df['label']==1).sum()/len(df)*100:.1f}%)")
    print(f"   Saved to: {output_file}")
    
    return df


def generate_test_data(n_samples: int = 100, output_path: str = "ai_model/datasets/test_data.csv"):
    """Generate test dataset riêng"""
    print(f"\nGenerating {n_samples} test samples...")
    df = generate_training_data(n_samples, output_path)
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("AI MODEL - DATA GENERATOR")
    print("=" * 60)
    
    # Generate training data
    train_df = generate_training_data(n_samples=500)
    
    # Generate test data
    test_df = generate_test_data(n_samples=100)
    
    # Display sample
    print("\n📊 Sample data:")
    print(train_df.head(10))
    
    print("\n" + "=" * 60)
    print("✅ Data generation completed!")
    print("=" * 60)
