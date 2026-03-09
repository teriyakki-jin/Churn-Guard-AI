"""
CI fixture generator: creates minimal model artifacts for testing.
Generates dummy .pkl files and reference CSV so the app can boot without real trained models.
Run from backend/ directory before pytest.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.dummy import DummyClassifier

# backend/ directory (one level up from tests/)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Feature names produced by train_model_v2.py's preprocess_data + pd.get_dummies
FEATURE_NAMES = [
    'SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges',
    'CustomerValueScore', 'ServiceCount', 'ContractStability', 'PaymentRisk',
    'ChargeRatio', 'AvgMonthlySpend', 'SeniorMonthly', 'PremiumServices', 'FiberNoSecurity',
    'gender_Female', 'gender_Male',
    'Partner_No', 'Partner_Yes',
    'Dependents_No', 'Dependents_Yes',
    'PhoneService_No', 'PhoneService_Yes',
    'MultipleLines_No', 'MultipleLines_No phone service', 'MultipleLines_Yes',
    'InternetService_DSL', 'InternetService_Fiber optic', 'InternetService_No',
    'OnlineSecurity_No', 'OnlineSecurity_No internet service', 'OnlineSecurity_Yes',
    'OnlineBackup_No', 'OnlineBackup_No internet service', 'OnlineBackup_Yes',
    'DeviceProtection_No', 'DeviceProtection_No internet service', 'DeviceProtection_Yes',
    'TechSupport_No', 'TechSupport_No internet service', 'TechSupport_Yes',
    'StreamingTV_No', 'StreamingTV_No internet service', 'StreamingTV_Yes',
    'StreamingMovies_No', 'StreamingMovies_No internet service', 'StreamingMovies_Yes',
    'Contract_Month-to-month', 'Contract_One year', 'Contract_Two year',
    'PaperlessBilling_No', 'PaperlessBilling_Yes',
    'PaymentMethod_Bank transfer (automatic)', 'PaymentMethod_Credit card (automatic)',
    'PaymentMethod_Electronic check', 'PaymentMethod_Mailed check',
    'TenureGroup_Growing', 'TenureGroup_Loyal', 'TenureGroup_Mature', 'TenureGroup_New',
]


def create_dummy_model():
    """Create a minimal DummyClassifier that satisfies predict_proba interface."""
    X = np.zeros((20, len(FEATURE_NAMES)))
    y = np.array([0, 1] * 10)
    model = DummyClassifier(strategy='uniform', random_state=42)
    model.fit(X, y)
    return model


def create_customer_churn_csv():
    """Create minimal Customer-Churn.csv used as normalization reference in engineer_features."""
    return pd.DataFrame({
        'customerID': ['0001-A', '0002-B', '0003-C', '0004-D', '0005-E'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
        'SeniorCitizen': [0, 0, 1, 0, 0],
        'Partner': ['Yes', 'No', 'No', 'Yes', 'No'],
        'Dependents': ['No', 'No', 'No', 'Yes', 'No'],
        'tenure': [1, 34, 2, 45, 2],
        'PhoneService': ['No', 'Yes', 'Yes', 'No', 'Yes'],
        'MultipleLines': ['No phone service', 'No', 'No', 'No phone service', 'No'],
        'InternetService': ['DSL', 'DSL', 'DSL', 'DSL', 'Fiber optic'],
        'OnlineSecurity': ['No', 'Yes', 'Yes', 'Yes', 'No'],
        'OnlineBackup': ['Yes', 'No', 'Yes', 'No', 'No'],
        'DeviceProtection': ['No', 'Yes', 'No', 'Yes', 'No'],
        'TechSupport': ['No', 'No', 'No', 'Yes', 'No'],
        'StreamingTV': ['No', 'No', 'No', 'No', 'No'],
        'StreamingMovies': ['No', 'No', 'No', 'No', 'No'],
        'Contract': ['Month-to-month', 'One year', 'Month-to-month', 'One year', 'Month-to-month'],
        'PaperlessBilling': ['Yes', 'No', 'Yes', 'No', 'Yes'],
        'PaymentMethod': [
            'Electronic check', 'Mailed check', 'Mailed check',
            'Bank transfer (automatic)', 'Electronic check',
        ],
        'MonthlyCharges': [29.85, 56.95, 53.85, 42.30, 70.70],
        'TotalCharges': [29.85, 1889.5, 108.15, 1840.75, 151.65],
        'Churn': ['No', 'No', 'Yes', 'No', 'Yes'],
    })


def main():
    print("Creating CI test fixtures...")

    # 1. data/Customer-Churn.csv
    data_dir = os.path.join(BACKEND_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, 'Customer-Churn.csv')
    create_customer_churn_csv().to_csv(csv_path, index=False)
    print(f"  [OK] data/Customer-Churn.csv")

    # 2. churn_model_v2.pkl + churn_model_candidate.pkl
    model = create_dummy_model()
    joblib.dump(model, os.path.join(BACKEND_DIR, 'churn_model_v2.pkl'))
    joblib.dump(model, os.path.join(BACKEND_DIR, 'churn_model_candidate.pkl'))
    print(f"  [OK] churn_model_v2.pkl + churn_model_candidate.pkl  (DummyClassifier, {len(FEATURE_NAMES)} features)")

    # 3. feature_names_v2.pkl
    joblib.dump(FEATURE_NAMES, os.path.join(BACKEND_DIR, 'feature_names_v2.pkl'))
    print(f"  [OK] feature_names_v2.pkl  ({len(FEATURE_NAMES)} features)")

    # 4. model_metadata_v2.json  (optional — avoids None-check warnings)
    metadata = {
        'version': '2.0-ci-dummy',
        'created_at': datetime.now().isoformat(),
        'ensemble_metrics': {
            'accuracy': 0.0, 'precision': 0.0,
            'recall': 0.0, 'f1': 0.0, 'roc_auc': 0.5,
        },
        'feature_count': len(FEATURE_NAMES),
    }
    with open(os.path.join(BACKEND_DIR, 'model_metadata_v2.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  [OK] model_metadata_v2.json")

    print("Fixtures ready.")


if __name__ == '__main__':
    main()
