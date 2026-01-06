"""
AI Model Training Script
Train Decision Tree classifier để phân loại Normal/Suspicious
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_data(data_path: str = "ai_model/datasets/training_data.csv"):
    """Load training data"""
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"  ✓ Loaded {len(df)} samples")
    return df


def prepare_features(df: pd.DataFrame):
    """Prepare X and y for training"""
    print("\nPreparing features...")
    
    # Feature columns
    feature_cols = [
        'hour',
        'day_of_week',
        'is_weekend',
        'is_night',
        'frequency_5min',
        'duration'
    ]
    
    X = df[feature_cols]
    y = df['label']
    
    print(f"  ✓ Features: {feature_cols}")
    print(f"  ✓ X shape: {X.shape}")
    print(f"  ✓ y shape: {y.shape}")
    print(f"  ✓ Class distribution:")
    print(f"    Normal (0): {(y==0).sum()} ({(y==0).sum()/len(y)*100:.1f}%)")
    print(f"    Suspicious (1): {(y==1).sum()} ({(y==1).sum()/len(y)*100:.1f}%)")
    
    return X, y, feature_cols


def train_decision_tree(X_train, y_train, X_test, y_test):
    """Train Decision Tree model"""
    print("\n[Model 1] Training Decision Tree...")
    
    model = DecisionTreeClassifier(
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Evaluation
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    
    print(f"  Training Accuracy: {train_acc:.3f}")
    print(f"  Test Accuracy: {test_acc:.3f}")
    
    return model, y_pred_test


def train_random_forest(X_train, y_train, X_test, y_test):
    """Train Random Forest model"""
    print("\n[Model 2] Training Random Forest...")
    
    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Evaluation
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    
    print(f"  Training Accuracy: {train_acc:.3f}")
    print(f"  Test Accuracy: {test_acc:.3f}")
    
    return model, y_pred_test


def evaluate_model(model, X_test, y_test, y_pred):
    """Detailed model evaluation"""
    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)
    
    # Classification Report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Suspicious']))
    
    # Confusion Matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print(f"\nTrue Negatives (Normal correctly classified): {cm[0,0]}")
    print(f"False Positives (Normal classified as Suspicious): {cm[0,1]}")
    print(f"False Negatives (Suspicious classified as Normal): {cm[1,0]}")
    print(f"True Positives (Suspicious correctly classified): {cm[1,1]}")
    
    # Feature Importance (if available)
    if hasattr(model, 'feature_importances_'):
        print("\nFeature Importances:")
        for feature, importance in zip(['hour', 'day_of_week', 'is_weekend', 'is_night', 'frequency_5min', 'duration'], 
                                       model.feature_importances_):
            print(f"  {feature}: {importance:.4f}")
    
    return cm


def save_model(model, feature_cols, model_path: str = "ai_model/models/classifier.pkl"):
    """Save trained model"""
    output_file = Path(model_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save model và metadata
    model_data = {
        'model': model,
        'feature_columns': feature_cols,
        'model_type': type(model).__name__
    }
    
    joblib.dump(model_data, output_file)
    print(f"\n✅ Model saved to: {output_file}")


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("AI MODEL TRAINING")
    print("=" * 60)
    
    # Load data
    df = load_data()
    
    # Prepare features
    X, y, feature_cols = prepare_features(df)
    
    # Split data
    print("\nSplitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train size: {len(X_train)}")
    print(f"  Test size: {len(X_test)}")
    
    # Train models
    dt_model, dt_pred = train_decision_tree(X_train, y_train, X_test, y_test)
    rf_model, rf_pred = train_random_forest(X_train, y_train, X_test, y_test)
    
    # Compare models
    dt_acc = accuracy_score(y_test, dt_pred)
    rf_acc = accuracy_score(y_test, rf_pred)
    
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print(f"Decision Tree Accuracy: {dt_acc:.3f}")
    print(f"Random Forest Accuracy: {rf_acc:.3f}")
    
    # Choose best model
    if rf_acc > dt_acc:
        print("\n✓ Selected: Random Forest")
        best_model = rf_model
        best_pred = rf_pred
    else:
        print("\n✓ Selected: Decision Tree")
        best_model = dt_model
        best_pred = dt_pred
    
    # Evaluate best model
    evaluate_model(best_model, X_test, y_test, best_pred)
    
    # Save best model
    save_model(best_model, feature_cols)
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETED!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review model performance above")
    print("  2. Test with: python ai_model/evaluate.py")
    print("  3. Integrate into backend")


if __name__ == "__main__":
    # Generate data first if not exists
    data_file = Path("ai_model/datasets/training_data.csv")
    if not data_file.exists():
        print("Training data not found. Generating...")
        from ai_model.data_generator import generate_training_data
        generate_training_data()
        print()
    
    main()
