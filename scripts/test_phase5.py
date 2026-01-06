"""
Phase 5 Complete Test Script
Test toàn bộ AI/ML pipeline: Data → Training → Evaluation → Prediction
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("PHASE 5: AI/ML IMPLEMENTATION - COMPLETE TEST")
print("=" * 70)

# Step 1: Generate training data
print("\n[STEP 1] Generating training data...")
print("-" * 70)
from ai_model.data_generator import generate_training_data, generate_test_data

train_df = generate_training_data(n_samples=500)
test_df = generate_test_data(n_samples=100)

# Step 2: Test feature engineering
print("\n[STEP 2] Testing feature engineering...")
print("-" * 70)
from backend.services.feature_engineering import FeatureEngineer
from backend.core.models import MotionEvent
from backend.core.enums import MotionStatus

test_event = MotionEvent(
    timestamp="2026-01-06T20:30:00Z",
    motion=MotionStatus.MOTION_DETECTED,
    sensor_id="TEST",
    location="living_room"
)

features = FeatureEngineer.extract_all_features(test_event)
print("Sample features extracted:")
for key, value in features.items():
    print(f"  {key}: {value}")

# Step 3: Train model
print("\n[STEP 3] Training ML model...")
print("-" * 70)
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load data
df = pd.read_csv("ai_model/datasets/training_data.csv")

# Prepare features
feature_cols = ['hour', 'day_of_week', 'is_weekend', 'is_night', 'frequency_5min', 'duration']
X = df[feature_cols]
y = df['label']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train Random Forest
print("Training Random Forest...")
model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {accuracy:.3f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Suspicious']))

# Save model
model_path = Path("ai_model/models/classifier.pkl")
model_path.parent.mkdir(parents=True, exist_ok=True)
model_data = {
    'model': model,
    'feature_columns': feature_cols,
    'model_type': 'RandomForestClassifier'
}
joblib.dump(model_data, model_path)
print(f"\nModel saved to: {model_path}")

# Step 4: Test AI Service
print("\n[STEP 4] Testing AI Service...")
print("-" * 70)
from backend.services.ai_service import AIService

ai_service = AIService()

test_scenarios = [
    ('Morning commute (7h)', '2026-01-06T07:30:00Z'),
    ('Late night motion (2h)', '2026-01-06T02:30:00Z'),
    ('Work hours intrusion (14h)', '2026-01-06T14:00:00Z'),
    ('Evening activity (20h)', '2026-01-06T20:00:00Z')
]

print("\nPrediction Results:")
for name, timestamp in test_scenarios:
    event = MotionEvent(
        timestamp=timestamp,
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="TEST",
        location="living_room"
    )
    
    result = ai_service.predict(event)
    status = "SUSPICIOUS" if result.is_abnormal else "NORMAL"
    symbol = "🔴" if result.is_abnormal else "🟢"
    
    print(f"\n  {name}")
    print(f"    Prediction: {symbol} {status}")
    print(f"    Confidence: {result.confidence:.2%}")
    print(f"    Alert: {result.alert_level.value.upper()}")

# Summary
print("\n" + "=" * 70)
print("PHASE 5 SUMMARY")
print("=" * 70)
print("\nCompleted Components:")
print("  ✅ Data Generator - 500 training + 100 test samples")
print("  ✅ Feature Engineering - 6 features extracted")
print(f"  ✅ ML Model - Random Forest ({accuracy:.1%} accuracy)")
print("  ✅ AI Service - Real-time prediction ready")

print("\nModel Performance:")
print(f"  - Training samples: {len(X_train)}")
print(f"  - Test samples: {len(X_test)}")
print(f"  - Test Accuracy: {accuracy:.3f}")
print(f"  - Normal class: {(y_test==0).sum()} samples")
print(f"  - Suspicious class: {(y_test==1).sum()} samples")

print("\nNext Steps:")
print("  1. Integrate AI Service into backend/main.py")
print("  2. Test end-to-end: PIR → MQTT → Backend → AI → Dashboard")
print("  3. Proceed to Phase 6: Dashboard")

print("\n" + "=" * 70)
print("✅ PHASE 5 COMPLETED SUCCESSFULLY!")
print("=" * 70)
