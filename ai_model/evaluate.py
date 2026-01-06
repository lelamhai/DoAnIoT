"""
AI Model Evaluation Script
Đánh giá model trên test data và demo predictions
"""

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_model(model_path: str = "ai_model/models/classifier.pkl"):
    """Load trained model"""
    print(f"Loading model from {model_path}...")
    model_data = joblib.load(model_path)
    print(f"  ✓ Model type: {model_data['model_type']}")
    print(f"  ✓ Features: {model_data['feature_columns']}")
    return model_data


def evaluate_on_test_data(model_data):
    """Evaluate model on test dataset"""
    print("\n" + "=" * 60)
    print("EVALUATION ON TEST DATA")
    print("=" * 60)
    
    # Load test data
    test_df = pd.read_csv("ai_model/datasets/test_data.csv")
    print(f"\nTest samples: {len(test_df)}")
    
    # Prepare features
    X_test = test_df[model_data['feature_columns']]
    y_test = test_df['label']
    
    # Predictions
    y_pred = model_data['model'].predict(X_test)
    y_proba = model_data['model'].predict_proba(X_test)
    
    # Metrics
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Suspicious']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    return test_df, y_pred, y_proba


def demo_predictions(model_data):
    """Demo with realistic scenarios"""
    print("\n" + "=" * 60)
    print("DEMO PREDICTIONS")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {
            'name': '1. Sáng đi làm (7h, thứ 2)',
            'hour': 7,
            'day_of_week': 0,
            'is_weekend': 0,
            'is_night': 0,
            'frequency_5min': 15,
            'duration': 5
        },
        {
            'name': '2. Tối về nhà (20h, thứ 5)',
            'hour': 20,
            'day_of_week': 3,
            'is_weekend': 0,
            'is_night': 0,
            'frequency_5min': 20,
            'duration': 10
        },
        {
            'name': '3. ĐÊM KHUYA CÓ CHUYỂN ĐỘNG (2h)',
            'hour': 2,
            'day_of_week': 2,
            'is_weekend': 0,
            'is_night': 1,
            'frequency_5min': 8,
            'duration': 45
        },
        {
            'name': '4. GIỜ LÀM VIỆC CÓ NGƯỜI (14h, thứ 3)',
            'hour': 14,
            'day_of_week': 1,
            'is_weekend': 0,
            'is_night': 0,
            'frequency_5min': 12,
            'duration': 30
        },
        {
            'name': '5. Cuối tuần ban ngày (11h, Chủ nhật)',
            'hour': 11,
            'day_of_week': 6,
            'is_weekend': 1,
            'is_night': 0,
            'frequency_5min': 25,
            'duration': 15
        },
        {
            'name': '6. Đêm muộn nhẹ (23h)',
            'hour': 23,
            'day_of_week': 4,
            'is_weekend': 0,
            'is_night': 1,
            'frequency_5min': 5,
            'duration': 3
        }
    ]
    
    for scenario in scenarios:
        name = scenario.pop('name')
        
        # Prepare features
        X = pd.DataFrame([scenario])
        
        # Predict
        pred = model_data['model'].predict(X)[0]
        proba = model_data['model'].predict_proba(X)[0]
        
        # Display
        print(f"\n{name}")
        print(f"  Features: {scenario}")
        print(f"  Prediction: {'🔴 SUSPICIOUS' if pred == 1 else '🟢 NORMAL'}")
        print(f"  Confidence: Normal={proba[0]:.2%}, Suspicious={proba[1]:.2%}")


def main():
    """Main evaluation pipeline"""
    print("=" * 60)
    print("AI MODEL EVALUATION")
    print("=" * 60)
    
    # Load model
    model_data = load_model()
    
    # Evaluate on test data
    test_df, y_pred, y_proba = evaluate_on_test_data(model_data)
    
    # Demo predictions
    demo_predictions(model_data)
    
    print("\n" + "=" * 60)
    print("✅ EVALUATION COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    # Check if model exists
    model_file = Path("ai_model/models/classifier.pkl")
    if not model_file.exists():
        print("❌ Model not found. Please train first:")
        print("   python ai_model/train.py")
        sys.exit(1)
    
    main()
