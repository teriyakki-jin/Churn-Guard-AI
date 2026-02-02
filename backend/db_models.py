from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    predictions = relationship("PredictionHistory", back_populates="user")

class Customer(Base):
    """고객 정보 모델"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    
    # 인구통계 정보
    gender = Column(String)
    senior_citizen = Column(Integer)
    partner = Column(String)
    dependents = Column(String)
    
    # 서비스 정보
    tenure = Column(Integer)
    phone_service = Column(String)
    multiple_lines = Column(String)
    internet_service = Column(String)
    online_security = Column(String)
    online_backup = Column(String)
    device_protection = Column(String)
    tech_support = Column(String)
    streaming_tv = Column(String)
    streaming_movies = Column(String)
    
    # 계약 정보
    contract = Column(String)
    paperless_billing = Column(String)
    payment_method = Column(String)
    monthly_charges = Column(Float)
    total_charges = Column(Float)
    
    # 이탈 여부
    churn = Column(Boolean, default=False)
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    predictions = relationship("PredictionHistory", back_populates="customer")

class PredictionHistory(Base):
    """예측 이력 모델"""
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 외래키
    user_id = Column(Integer, ForeignKey("users.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    # 예측 결과
    churn_probability = Column(Float)
    prediction = Column(String)  # "Yes" or "No"
    risk_level = Column(String)  # "Low", "Moderate", "High"
    
    # 추천 전략
    suggestions = Column(String)  # JSON 형태로 저장
    
    # 메타데이터
    model_version = Column(String)
    prediction_date = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User", back_populates="predictions")
    customer = relationship("Customer", back_populates="predictions")

class ModelMetrics(Base):
    """모델 성능 지표"""
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String, nullable=False)
    
    # 성능 지표
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    
    # 메타데이터
    training_date = Column(DateTime, default=datetime.utcnow)
    training_samples = Column(Integer)
    feature_importance = Column(String)  # JSON 형태
    
    # 설명
    notes = Column(String)
