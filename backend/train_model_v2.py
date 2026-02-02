"""
Churn Model v2 - Phase 2 Improvements
- Feature Engineering
- Ensemble Model (XGBoost + RandomForest + GradientBoosting)
- Hyperparameter Tuning with GridSearchCV
"""
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score, classification_report, roc_auc_score,
    precision_score, recall_score, f1_score, confusion_matrix
)
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
from datetime import datetime

# ============== Configuration ==============
DATA_PATH = 'data/Customer-Churn.csv'
MODEL_OUTPUT_DIR = '.'
RANDOM_STATE = 42

# ============== Feature Engineering ==============
def engineer_features(df):
    """Create new features for better prediction."""
    df = df.copy()

    # 1. Customer Value Score
    max_charges = df['MonthlyCharges'].max()
    max_total = df['TotalCharges'].max()
    df['CustomerValueScore'] = (
        df['tenure'] * 0.3 +
        (df['MonthlyCharges'] / max_charges) * 100 * 0.4 +
        (df['TotalCharges'] / max_total) * 100 * 0.3
    )

    # 2. Service Count (how many services customer uses)
    service_cols = [
        'PhoneService', 'MultipleLines', 'InternetService',
        'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
        'TechSupport', 'StreamingTV', 'StreamingMovies'
    ]
    df['ServiceCount'] = 0
    for col in service_cols:
        if col in df.columns:
            df['ServiceCount'] += (df[col].isin(['Yes', 'DSL', 'Fiber optic'])).astype(int)

    # 3. Contract Stability Score
    contract_map = {'Month-to-month': 1, 'One year': 2, 'Two year': 3}
    df['ContractStability'] = df['Contract'].map(contract_map).fillna(1)

    # 4. Payment Risk Score
    payment_map = {
        'Electronic check': 3,
        'Mailed check': 2,
        'Bank transfer (automatic)': 1,
        'Credit card (automatic)': 1
    }
    df['PaymentRisk'] = df['PaymentMethod'].map(payment_map).fillna(2)

    # 5. Tenure Groups
    df['TenureGroup'] = pd.cut(
        df['tenure'],
        bins=[0, 12, 24, 48, 72],
        labels=['New', 'Growing', 'Mature', 'Loyal']
    ).astype(str)

    # 6. Monthly Charges to Total Charges Ratio
    df['ChargeRatio'] = np.where(
        df['TotalCharges'] > 0,
        df['MonthlyCharges'] / (df['TotalCharges'] / np.maximum(df['tenure'], 1)),
        1
    )

    # 7. Average Monthly Spend
    df['AvgMonthlySpend'] = np.where(
        df['tenure'] > 0,
        df['TotalCharges'] / df['tenure'],
        df['MonthlyCharges']
    )

    # 8. Is Senior with Month-to-Month (High Risk Segment)
    df['SeniorMonthly'] = ((df['SeniorCitizen'] == 1) &
                           (df['Contract'] == 'Month-to-month')).astype(int)

    # 9. Has Premium Services
    premium_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport']
    df['PremiumServices'] = 0
    for col in premium_cols:
        if col in df.columns:
            df['PremiumServices'] += (df[col] == 'Yes').astype(int)

    # 10. Fiber with No Security (Risk indicator)
    df['FiberNoSecurity'] = (
        (df['InternetService'] == 'Fiber optic') &
        (df['OnlineSecurity'] == 'No')
    ).astype(int)

    return df


def preprocess_data(df):
    """Clean and preprocess data."""
    df = df.copy()

    # Handle TotalCharges
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'].fillna(df['TotalCharges'].mean(), inplace=True)

    # Drop customerID
    if 'customerID' in df.columns:
        df.drop('customerID', axis=1, inplace=True)

    # Apply feature engineering
    df = engineer_features(df)

    # Encode target
    df['Churn'] = df['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)

    # One-hot encode categorical variables
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    df = pd.get_dummies(df, columns=categorical_cols)

    return df


# ============== Model Training ==============
def train_ensemble_model(X_train, y_train):
    """Train ensemble model with hyperparameter tuning."""
    print("\n" + "="*50)
    print("Training Ensemble Model with Hyperparameter Tuning")
    print("="*50)

    # 1. XGBoost with GridSearchCV
    print("\n[1/3] Tuning XGBoost...")
    xgb_params = {
        'n_estimators': [100, 200],
        'max_depth': [4, 6],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.8, 0.9]
    }

    xgb_model = xgb.XGBClassifier(
        random_state=RANDOM_STATE,
        use_label_encoder=False,
        eval_metric='logloss'
    )

    xgb_grid = GridSearchCV(
        xgb_model, xgb_params, cv=3, scoring='roc_auc', n_jobs=-1, verbose=1
    )
    xgb_grid.fit(X_train, y_train)
    best_xgb = xgb_grid.best_estimator_
    print(f"Best XGBoost params: {xgb_grid.best_params_}")
    print(f"Best XGBoost ROC-AUC: {xgb_grid.best_score_:.4f}")

    # 2. Random Forest
    print("\n[2/3] Tuning Random Forest...")
    rf_params = {
        'n_estimators': [100, 200],
        'max_depth': [6, 10],
        'min_samples_split': [2, 5]
    }

    rf_model = RandomForestClassifier(random_state=RANDOM_STATE)
    rf_grid = GridSearchCV(
        rf_model, rf_params, cv=3, scoring='roc_auc', n_jobs=-1, verbose=1
    )
    rf_grid.fit(X_train, y_train)
    best_rf = rf_grid.best_estimator_
    print(f"Best RF params: {rf_grid.best_params_}")
    print(f"Best RF ROC-AUC: {rf_grid.best_score_:.4f}")

    # 3. Gradient Boosting
    print("\n[3/3] Tuning Gradient Boosting...")
    gb_params = {
        'n_estimators': [100, 150],
        'max_depth': [3, 5],
        'learning_rate': [0.05, 0.1]
    }

    gb_model = GradientBoostingClassifier(random_state=RANDOM_STATE)
    gb_grid = GridSearchCV(
        gb_model, gb_params, cv=3, scoring='roc_auc', n_jobs=-1, verbose=1
    )
    gb_grid.fit(X_train, y_train)
    best_gb = gb_grid.best_estimator_
    print(f"Best GB params: {gb_grid.best_params_}")
    print(f"Best GB ROC-AUC: {gb_grid.best_score_:.4f}")

    # 4. Create Voting Ensemble
    print("\n[4/4] Creating Voting Ensemble...")
    ensemble = VotingClassifier(
        estimators=[
            ('xgb', best_xgb),
            ('rf', best_rf),
            ('gb', best_gb)
        ],
        voting='soft',
        weights=[2, 1, 1]  # XGBoost gets more weight
    )
    ensemble.fit(X_train, y_train)

    return ensemble, {
        'xgb_params': xgb_grid.best_params_,
        'rf_params': rf_grid.best_params_,
        'gb_params': gb_grid.best_params_,
        'xgb_score': xgb_grid.best_score_,
        'rf_score': rf_grid.best_score_,
        'gb_score': gb_grid.best_score_
    }


def evaluate_model(model, X_test, y_test, model_name="Model"):
    """Comprehensive model evaluation."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_prob)
    }

    print(f"\n{'='*50}")
    print(f"{model_name} Evaluation Results")
    print('='*50)
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1-Score:  {metrics['f1']:.4f}")
    print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    return metrics


def get_feature_importance(model, feature_names):
    """Extract feature importance from ensemble."""
    # Get XGBoost feature importance (first estimator)
    xgb_model = model.named_estimators_['xgb']
    importance = xgb_model.feature_importances_

    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)

    return importance_df


# ============== Main Training Pipeline ==============
def main():
    print("="*60)
    print("Churn Model v2 - Training Pipeline")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Load data
    print("\n[Step 1] Loading data...")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} records")

    # Preprocess
    print("\n[Step 2] Preprocessing & Feature Engineering...")
    df_processed = preprocess_data(df)
    print(f"Created {len(df_processed.columns)} features (including engineered)")

    # Split features and target
    X = df_processed.drop('Churn', axis=1)
    y = df_processed['Churn']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # Train baseline XGBoost for comparison
    print("\n[Step 3] Training Baseline Model...")
    baseline = xgb.XGBClassifier(
        n_estimators=100, max_depth=4, learning_rate=0.1,
        random_state=RANDOM_STATE, use_label_encoder=False, eval_metric='logloss'
    )
    baseline.fit(X_train, y_train)
    baseline_metrics = evaluate_model(baseline, X_test, y_test, "Baseline XGBoost")

    # Train ensemble model
    print("\n[Step 4] Training Ensemble Model...")
    ensemble, tuning_results = train_ensemble_model(X_train, y_train)
    ensemble_metrics = evaluate_model(ensemble, X_test, y_test, "Ensemble Model")

    # Compare results
    print("\n" + "="*60)
    print("Performance Comparison")
    print("="*60)
    print(f"{'Metric':<15} {'Baseline':<12} {'Ensemble':<12} {'Improvement':<12}")
    print("-"*51)
    for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
        base = baseline_metrics[metric]
        ens = ensemble_metrics[metric]
        imp = ((ens - base) / base) * 100
        print(f"{metric:<15} {base:<12.4f} {ens:<12.4f} {imp:+.2f}%")

    # Feature importance
    print("\n[Step 5] Analyzing Feature Importance...")
    importance_df = get_feature_importance(ensemble, X.columns.tolist())
    print("\nTop 15 Important Features:")
    print(importance_df.head(15).to_string(index=False))

    # Save model and artifacts
    print("\n[Step 6] Saving Model & Artifacts...")

    # Save ensemble model
    joblib.dump(ensemble, f'{MODEL_OUTPUT_DIR}/churn_model_v2.pkl')
    print(f"Saved: churn_model_v2.pkl")

    # Save feature names
    joblib.dump(X.columns.tolist(), f'{MODEL_OUTPUT_DIR}/feature_names_v2.pkl')
    print(f"Saved: feature_names_v2.pkl")

    # Save model metadata
    metadata = {
        'version': '2.0',
        'created_at': datetime.now().isoformat(),
        'baseline_metrics': baseline_metrics,
        'ensemble_metrics': ensemble_metrics,
        'tuning_results': {k: str(v) for k, v in tuning_results.items()},
        'feature_count': len(X.columns),
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }

    with open(f'{MODEL_OUTPUT_DIR}/model_metadata_v2.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved: model_metadata_v2.json")

    # Save feature importance
    importance_df.to_csv(f'{MODEL_OUTPUT_DIR}/feature_importance_v2.csv', index=False)
    print(f"Saved: feature_importance_v2.csv")

    print("\n" + "="*60)
    print("Training Complete!")
    print(f"Final ROC-AUC: {ensemble_metrics['roc_auc']:.4f}")
    print("="*60)

    return ensemble, ensemble_metrics


if __name__ == "__main__":
    model, metrics = main()
