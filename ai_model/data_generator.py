"""
AI Model - Data Generator
Tạo synthetic dataset để train model phân loại Normal/Suspicious
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import yaml


def load_time_config():
    """Load time configuration from YAML file"""
    config_path = Path("config/time_config.yaml")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config['time_rules']['suspicious_hours']
    else:
        # Default fallback
        return {'start': 15, 'end': 18}


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
    
    # Load time configuration
    time_config = load_time_config()
    suspicious_start = time_config['start']  # 15
    suspicious_end = time_config['end']      # 18
    
    print(f"   Using time config: SUSPICIOUS hours = {suspicious_start}h-{suspicious_end}h")
    
    data = []
    start_date = datetime(2026, 1, 1, 0, 0, 0)
    
    for i in range(n_samples):
        # Random timestamp trong 30 ngày
        days_offset = np.random.randint(0, 30)
        hour = np.random.randint(0, 24)
        minute = np.random.randint(0, 60)
        
        timestamp = start_date + timedelta(days=days_offset, hours=hour, minutes=minute)
        day_of_week = timestamp.weekday()  # 0=Monday, 6=Sunday
        
        # Tạo patterns dựa trên time config
        
        # SUSPICIOUS PATTERNS (15h-18h)
        if suspicious_start <= hour < suspicious_end:
            motion = np.random.choice([0, 1], p=[0.2, 0.8])  # 80% có chuyển động
            if motion == 1:
                label = 1  # SUSPICIOUS - chuyển động trong 15h-18h
                frequency = np.random.randint(15, 35)
                duration = np.random.uniform(10, 60)  # Lâu hơn
            else:
                label = 0  # Normal - không có chuyển động
                frequency = 0
                duration = 0
        
        # NORMAL PATTERNS (ngoài 15h-18h)
        else:
            motion = np.random.choice([0, 1], p=[0.3, 0.7])  # 70% có chuyển động
            label = 0  # Normal
            frequency = np.random.randint(10, 30)  # Tần suất bình thường
            duration = np.random.uniform(3, 12)  # 3-12 giây
        
        # Add noise - realistic imperfections
        if np.random.random() < 0.05:  # 5% noise
            label = 1 - label  # Flip label
        
        data.append({
            'timestamp': timestamp.isoformat(),
            'motion': motion,
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': 1 if day_of_week >= 5 else 0,
            'is_night': 1 if (suspicious_start <= hour < suspicious_end) else 0,
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
