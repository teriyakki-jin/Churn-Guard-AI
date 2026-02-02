import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_auc_score, roc_curve, precision_recall_curve
)
from sklearn.preprocessing import StandardScaler
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class ImprovedChurnModel:
    """개선된 이탈 예측 모델"""
    
    def __init__(self, model_version="v2.0"):
        self.model_version = model_version
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.metrics = {}
        
    def load_and_preprocess_data(self, filepath='backend/data/Customer-Churn.csv'):
        """데이터 로드 및 전처리"""
        print("📊 Loading data...")
        df = pd.read_csv(filepath)
        
        # TotalCharges 처리
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(df['TotalCharges'].median(), inplace=True)
        
        # customerID 제거
        if 'customerID' in df.columns:
            df.drop('customerID', axis=1, inplace=True)
        
        # 타겟 변수 인코딩
        df['Churn'] = df['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)
        
        # Feature Engineering
        print("🔧 Engineering features...")
        
        # 1. 고객 가치 점수
        df['customer_value_score'] = (
            df['tenure'] * 0.3 + 
            (df['MonthlyCharges'] / df['MonthlyCharges'].max()) * 100 * 0.4 +
            (df['TotalCharges'] / df['TotalCharges'].max()) * 100 * 0.3
        )
        
        # 2. 서비스 사용량
        service_cols = ['PhoneService', 'MultipleLines', 'InternetService', 
                       'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                       'TechSupport', 'StreamingTV', 'StreamingMovies']
        df['total_services'] = df[service_cols].apply(
            lambda x: sum([1 for val in x if val not in ['No', 'No internet service', 'No phone service']]), 
            axis=1
        )
        
        # 3. 월별 지출 대비 총 지출 비율
        df['charge_ratio'] = df['TotalCharges'] / (df['MonthlyCharges'] * df['tenure'] + 1)
        
        # 4. 계약 안정성 점수
        contract_scores = {'Month-to-month': 1, 'One year': 2, 'Two year': 3}
        df['contract_stability'] = df['Contract'].map(contract_scores)
        
        # 5. 결제 방식 위험도
        payment_risk = {
            'Electronic check': 3,
            'Mailed check': 2,
            'Bank transfer (automatic)': 1,
            'Credit card (automatic)': 1
        }
        df['payment_risk'] = df['PaymentMethod'].map(payment_risk)
        
        # One-hot encoding
        categorical_cols = df.select_dtypes(include=['object']).columns
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        # 특성과 타겟 분리
        X = df.drop('Churn', axis=1)
        y = df['Churn']
        
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def train_ensemble_model(self, X_train, y_train):
        """앙상블 모델 학습"""
        print("🎯 Training ensemble model...")
        
        # 개별 모델 정의
        xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        gb_model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=5,
            random_state=42
        )
        
        # 투표 앙상블
        self.model = VotingClassifier(
            estimators=[
                ('xgb', xgb_model),
                ('rf', rf_model),
                ('gb', gb_model)
            ],
            voting='soft',
            weights=[2, 1, 1]  # XGBoost에 더 높은 가중치
        )
        
        self.model.fit(X_train, y_train)
        print("✅ Ensemble model trained successfully!")
        
    def evaluate_model(self, X_test, y_test):
        """모델 평가"""
        print("📈 Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # 성능 지표 계산
        self.metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'roc_auc': float(roc_auc_score(y_test, y_pred_proba)),
            'precision': float(classification_report(y_test, y_pred, output_dict=True)['1']['precision']),
            'recall': float(classification_report(y_test, y_pred, output_dict=True)['1']['recall']),
            'f1_score': float(classification_report(y_test, y_pred, output_dict=True)['1']['f1-score'])
        }
        
        print("\n🎯 Model Performance:")
        print(f"Accuracy:  {self.metrics['accuracy']:.4f}")
        print(f"ROC-AUC:   {self.metrics['roc_auc']:.4f}")
        print(f"Precision: {self.metrics['precision']:.4f}")
        print(f"Recall:    {self.metrics['recall']:.4f}")
        print(f"F1-Score:  {self.metrics['f1_score']:.4f}")
        
        print("\n📊 Classification Report:")
        print(classification_report(y_test, y_pred))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\n🔢 Confusion Matrix:")
        print(cm)
        
        return self.metrics
    
    def get_feature_importance(self):
        """특성 중요도 추출"""
        # XGBoost 모델의 특성 중요도 사용
        xgb_model = self.model.named_estimators_['xgb']
        importance = xgb_model.feature_importances_
        
        feature_importance = dict(zip(self.feature_names, importance))
        # 상위 15개만 추출
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:15]
        
        return dict(sorted_features)
    
    def save_model(self, output_dir='backend/models'):
        """모델 및 메타데이터 저장"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 모델 저장
        model_path = f"{output_dir}/churn_model_{timestamp}.pkl"
        joblib.dump(self.model, model_path)
        print(f"✅ Model saved: {model_path}")
        
        # Feature names 저장
        features_path = f"{output_dir}/feature_names_{timestamp}.pkl"
        joblib.dump(self.feature_names, features_path)
        
        # 최신 모델로 복사
        joblib.dump(self.model, 'backend/churn_model.pkl')
        joblib.dump(self.feature_names, 'backend/feature_names.pkl')
        
        # 메타데이터 저장
        metadata = {
            'model_version': self.model_version,
            'training_date': timestamp,
            'metrics': self.metrics,
            'feature_importance': self.get_feature_importance(),
            'n_features': len(self.feature_names)
        }
        
        metadata_path = f"{output_dir}/model_metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f"✅ Metadata saved: {metadata_path}")

def main():
    """메인 실행 함수"""
    print("🚀 Starting improved model training...\n")
    
    # 모델 초기화
    model = ImprovedChurnModel(model_version="v2.0")
    
    # 데이터 로드 및 전처리
    X, y = model.load_and_preprocess_data()
    
    # 데이터 분할 (stratify로 클래스 비율 유지)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📦 Train set: {X_train.shape}, Test set: {X_test.shape}")
    print(f"📊 Churn rate - Train: {y_train.mean():.2%}, Test: {y_test.mean():.2%}")
    
    # 모델 학습
    model.train_ensemble_model(X_train, y_train)
    
    # 모델 평가
    metrics = model.evaluate_model(X_test, y_test)
    
    # 특성 중요도
    print("\n🎯 Top Feature Importance:")
    for feature, importance in list(model.get_feature_importance().items())[:10]:
        print(f"  {feature}: {importance:.4f}")
    
    # 모델 저장
    model.save_model()
    
    print("\n✅ Training completed successfully!")

if __name__ == "__main__":
    main()
