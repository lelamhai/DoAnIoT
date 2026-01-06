"""
TRAIN DATA - MODULE 3: TRAINING AI MODEL
Chạy khi thay đổi config thời gian
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from pathlib import Path


def main():
    print("=" * 70)
    print("MODULE 3: TRAIN AI MODEL")
    print("=" * 70)
    
    # Step 1: Generate data
    print("\n[Bước 1/2] Generate training data...")
    print("            Đọc config từ: config/time_config.yaml")
    
    from ai_model.data_generator import generate_training_data, generate_test_data
    
    train_df = generate_training_data(n_samples=500)
    test_df = generate_test_data(n_samples=100)
    
    print(f"            ✓ Training: {len(train_df)} samples")
    print(f"            ✓ Test: {len(test_df)} samples")
    
    # Step 2: Train model
    print("\n[Bước 2/2] Train AI model...")
    
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    import joblib
    
    # Load data
    df = pd.read_csv('ai_model/datasets/training_data.csv')
    
    # Features
    X = df[['hour', 'day_of_week', 'is_weekend', 'is_night', 'frequency_5min', 'duration']]
    y = df['label']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    
    print(f"            ✓ Training Accuracy: {train_acc:.1%}")
    print(f"            ✓ Test Accuracy: {test_acc:.1%}")
    
    # Save model
    model_path = Path("ai_model/models/classifier.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    
    print(f"\n✓ Model saved: {model_path}")
    
    # Show classification report
    print("\n" + "=" * 70)
    print("CLASSIFICATION REPORT:")
    print("=" * 70)
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Suspicious']))
    
    print("\n" + "=" * 70)
    print("✓ HOÀN TẤT! Model đã sẵn sàng để sử dụng")
    print("=" * 70)
    print("\nBước tiếp theo:")
    print("  1. Chạy backend: python backend/simple_main.py")
    print("  2. Chạy frontend: streamlit run frontend/app.py")
    print("  3. Test: python scripts/mqtt_test_publisher.py")


if __name__ == "__main__":
    main()
