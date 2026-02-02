# Churn-Guard-AI 개선 계획서

## 📊 현재 상태 분석

### ✅ 강점
- XGBoost 기반 고성능 이탈 예측 모델
- 직관적인 React 기반 대시보드
- JWT 인증 시스템 구현
- 실시간 예측 기능
- 통계적 분석 제공

### ⚠️ 개선 필요 영역
1. **보안**: 하드코딩된 시크릿 키
2. **확장성**: 데이터베이스 미사용
3. **성능**: 단일 모델 사용
4. **테스트**: 테스트 코드 부재
5. **배포**: Docker 설정 부재
6. **모니터링**: 로깅 및 모니터링 미흡

---

## 🎯 개선 사항 상세

### 1. 보안 강화 (Priority: 🔴 High)

#### 현재 문제
```python
SECRET_KEY = "supersecretkey"  # 보안 취약
```

#### 해결 방안
```python
# .env 파일 사용
SECRET_KEY=randomly-generated-secure-key-change-this
ALGORITHM=HS256

# auth.py에서
from dotenv import load_dotenv
SECRET_KEY = os.getenv("SECRET_KEY")
```

**추가 보안 조치:**
- Rate limiting (slowapi)
- HTTPS 강제
- CORS 정책 강화
- 비밀번호 정책 (최소 8자, 특수문자 포함)
- 세션 타임아웃

---

### 2. 데이터베이스 통합 (Priority: 🔴 High)

#### 아키텍처
```
Users Table
├── id (PK)
├── username
├── email
├── hashed_password
└── created_at

Customers Table
├── id (PK)
├── customer_id
├── [고객 정보 필드들]
└── churn (boolean)

PredictionHistory Table
├── id (PK)
├── user_id (FK)
├── customer_id (FK)
├── churn_probability
├── prediction
├── risk_level
└── prediction_date
```

**장점:**
- 예측 이력 추적
- 다중 사용자 지원
- 데이터 영속성
- 감사 로그

---

### 3. 모델 성능 개선 (Priority: 🟡 Medium)

#### A. Feature Engineering

**신규 특성 추가:**
```python
# 1. 고객 가치 점수
customer_value_score = (
    tenure * 0.3 + 
    (monthly_charges / max_charges) * 100 * 0.4 +
    (total_charges / max_total) * 100 * 0.3
)

# 2. 서비스 사용 다양성
total_services = count_active_services()

# 3. 계약 안정성 점수
contract_stability = {
    'Month-to-month': 1,
    'One year': 2,
    'Two year': 3
}

# 4. 결제 위험도
payment_risk = {
    'Electronic check': 3,
    'Mailed check': 2,
    'Bank transfer': 1,
    'Credit card': 1
}
```

#### B. 앙상블 모델

**현재:** XGBoost 단일 모델  
**개선:** Voting Ensemble

```python
ensemble = VotingClassifier([
    ('xgb', XGBClassifier(n_estimators=200)),
    ('rf', RandomForestClassifier(n_estimators=200)),
    ('gb', GradientBoostingClassifier(n_estimators=150))
], voting='soft', weights=[2, 1, 1])
```

**예상 성능 향상:**
- Accuracy: 80% → 84%
- ROC-AUC: 0.84 → 0.88
- Precision: 65% → 72%
- Recall: 55% → 60%

#### C. 하이퍼파라미터 튜닝

```python
from sklearn.model_selection import GridSearchCV

params = {
    'n_estimators': [100, 200, 300],
    'max_depth': [4, 6, 8],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.7, 0.8, 0.9]
}

grid_search = GridSearchCV(
    xgb.XGBClassifier(),
    params,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1
)
```

---

### 4. API 개선 (Priority: 🟡 Medium)

#### A. 문서화

**FastAPI 자동 문서화 활용:**
```python
@app.post("/predict", 
    summary="고객 이탈 예측",
    description="고객 데이터를 기반으로 이탈 확률을 예측합니다.",
    response_description="이탈 확률, 위험도, 맞춤 전략"
)
async def predict_churn(data: CustomerData):
    """
    ## 고객 이탈 예측
    
    입력:
    - gender: 성별
    - tenure: 가입 기간 (개월)
    - contract: 계약 유형
    - ...
    
    출력:
    - churn_risk_score: 이탈 확률 (0~1)
    - prediction: Yes/No
    - suggestions: 맞춤 전략 리스트
    """
    ...
```

#### B. 에러 핸들링

```python
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid input data"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

#### C. Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/predict")
@limiter.limit("10/minute")
async def predict_churn(request: Request, data: CustomerData):
    ...
```

---

### 5. 테스트 코드 작성 (Priority: 🟡 Medium)

#### 테스트 구조
```
tests/
├── test_auth.py
├── test_prediction.py
├── test_models.py
└── test_integration.py
```

#### 예시: test_prediction.py
```python
import pytest
from fastapi.testclient import TestClient

def test_predict_high_risk():
    response = client.post("/predict", json={
        "contract": "Month-to-month",
        "payment_method": "Electronic check",
        "tenure": 2,
        ...
    })
    assert response.status_code == 200
    assert response.json()["churn_risk_score"] > 0.7

def test_predict_low_risk():
    response = client.post("/predict", json={
        "contract": "Two year",
        "payment_method": "Credit card (automatic)",
        "tenure": 36,
        ...
    })
    assert response.status_code == 200
    assert response.json()["churn_risk_score"] < 0.3
```

---

### 6. 프론트엔드 개선 (Priority: 🟢 Low)

#### A. 상태 관리

**Zustand 또는 Redux 도입:**
```javascript
// store.js
import create from 'zustand'

const useStore = create((set) => ({
  user: null,
  predictions: [],
  setUser: (user) => set({ user }),
  addPrediction: (prediction) => 
    set((state) => ({ 
      predictions: [...state.predictions, prediction] 
    }))
}))
```

#### B. 에러 바운더리

```javascript
class ErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  render() {
    if (this.state.hasError) {
      return <div>문제가 발생했습니다. 다시 시도해주세요.</div>;
    }
    return this.props.children;
  }
}
```

#### C. 로딩 상태 개선

```javascript
const { data, isLoading, error } = useQuery('stats', fetchStats)

if (isLoading) return <Skeleton />
if (error) return <ErrorMessage />
return <Dashboard data={data} />
```

---

### 7. 배포 전략 (Priority: 🟢 Low)

#### A. Docker Compose

**개발 환경:**
```bash
docker-compose up -d
```

**프로덕션 환경:**
```bash
docker-compose --profile production up -d
```

#### B. CI/CD 파이프라인 (GitHub Actions)

```yaml
name: CI/CD

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker-compose build
          docker-compose up -d
```

---

### 8. 모니터링 및 로깅 (Priority: 🟢 Low)

#### A. 구조화된 로깅

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
logger.addHandler(handler)

@app.post("/predict")
async def predict_churn(data: CustomerData):
    logger.info(f"Prediction request received: {data.dict()}")
    result = service.predict(data)
    logger.info(f"Prediction completed: {result['churn_risk_score']}")
    return result
```

#### B. 성능 모니터링

```python
import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request processed in {process_time:.2f}s")
    return response
```

---

## 📅 구현 로드맵

### Phase 1: 기초 강화 (1-2주)
- [ ] 환경 변수 설정 (.env)
- [ ] 데이터베이스 통합 (SQLAlchemy)
- [ ] 기본 테스트 코드 작성
- [ ] Docker 설정

### Phase 2: 성능 개선 (2-3주)
- [ ] Feature Engineering
- [ ] 앙상블 모델 구현
- [ ] 하이퍼파라미터 튜닝
- [ ] API 문서화 강화

### Phase 3: 운영 최적화 (2-3주)
- [ ] Rate Limiting
- [ ] 로깅 시스템 구축
- [ ] 에러 핸들링 강화
- [ ] CI/CD 파이프라인

### Phase 4: 고도화 (진행중)
- [ ] 모델 A/B 테스팅
- [ ] 실시간 대시보드 업데이트
- [ ] 알림 시스템 (이메일/슬랙)
- [ ] 고급 분석 리포트

---

## 💰 예상 효과

### 기술적 개선
- **모델 정확도**: 80% → 84% (+5%)
- **API 응답 속도**: 500ms → 200ms (-60%)
- **시스템 안정성**: 95% → 99.5% (+4.5%)

### 비즈니스 가치
- **이탈 방지율**: 20% → 35% (+75%)
- **고객 유지 비용**: $450 → $300 (-33%)
- **ROI**: $593 → $850 (+43%)

---

## 🚀 시작하기

### 1. 환경 설정
```bash
# 의존성 설치
cd backend
pip install -r requirements_improved.txt

cd ../frontend
npm install
```

### 2. 환경 변수 설정
```bash
# backend/.env 생성
cp .env.example .env
# SECRET_KEY 수정
```

### 3. 데이터베이스 초기화
```bash
python backend/database.py
```

### 4. 모델 재학습 (옵션)
```bash
python backend/train_model_improved.py
```

### 5. 실행
```bash
# Docker 사용
docker-compose up -d

# 또는 로컬 실행
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

---

## 📚 참고 자료

### 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [XGBoost 문서](https://xgboost.readthedocs.io/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

### 관련 논문
- Customer Churn Prediction using Machine Learning (2023)
- Ensemble Methods for Churn Prediction (2022)

### 유사 프로젝트
- [Telco Churn Prediction](https://github.com/IBM/telco-customer-churn-on-icp4d)
- [Churn Modeling](https://github.com/khanhnamle1994/customer-churn-prediction)

---

## 🤝 기여 방법

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 라이센스

MIT License - 자유롭게 사용 가능합니다.

---

**문의:** your-email@example.com  
**GitHub:** https://github.com/teriyakki-jin/Churn-Guard-AI
