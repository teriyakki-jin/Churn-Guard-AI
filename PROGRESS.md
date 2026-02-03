# Churn-Guard-AI 개발 진행 상황

> 마지막 업데이트: 2026-02-03

---

## 전체 로드맵

| Phase | 상태 | 완료율 |
|-------|------|--------|
| Phase 1: 기초 강화 | ✅ 완료 | 100% |
| Phase 2: 성능 개선 | ✅ 완료 | 100% |
| Phase 3: 운영 최적화 | ✅ 완료 | 100% |
| Phase 4: 고도화 | 🔄 진행중 | 60% |

---

## Phase 1: 기초 강화 ✅

### 1.1 환경 변수 설정 ✅
- `.env` 파일 구성
- `python-dotenv` 적용
- SECRET_KEY, ALGORITHM 환경변수화

### 1.2 데이터베이스 통합 ✅
- SQLAlchemy ORM 적용
- SQLite 기본 DB (PostgreSQL 옵션)
- User 테이블 구현

### 1.3 테스트 코드 작성 ✅
```
tests/
├── conftest.py          # pytest fixtures
├── test_main.py         # 루트 엔드포인트 테스트
├── test_auth.py         # 인증 테스트 (3개)
├── test_prediction.py   # 예측 API 테스트 (9개)
└── test_integration.py  # 통합 테스트 (6개)

총 19개 테스트 PASSED
```

### 1.4 Docker 설정 ✅
- `docker-compose.yml` - 전체 서비스 오케스트레이션
- `Dockerfile.springboot` - Spring Boot 빌드
- `backend/Dockerfile` - FastAPI 빌드
- `frontend/Dockerfile` - React 빌드
- `nginx/nginx.conf` - 프로덕션 리버스 프록시
- `.dockerignore` 파일들

---

## Phase 2: 성능 개선 ✅

### 2.1 Feature Engineering ✅
**10개 신규 특성 추가:**

| 특성명 | 설명 | 중요도 |
|--------|------|--------|
| CustomerValueScore | 고객 가치 점수 | - |
| ServiceCount | 사용 서비스 수 | - |
| ContractStability | 계약 안정성 점수 | **22.6%** |
| PaymentRisk | 결제 위험도 | 1.6% |
| TenureGroup | 고객 생애주기 그룹 | 2.2% |
| ChargeRatio | 청구 비율 | - |
| AvgMonthlySpend | 평균 월간 지출 | - |
| SeniorMonthly | 시니어+월정액 플래그 | - |
| PremiumServices | 프리미엄 서비스 수 | - |
| FiberNoSecurity | 광섬유+보안없음 위험 | **14.2%** |

### 2.2 앙상블 모델 구현 ✅
```python
VotingClassifier([
    ('xgb', XGBClassifier),      # 가중치: 2
    ('rf', RandomForestClassifier),  # 가중치: 1
    ('gb', GradientBoostingClassifier) # 가중치: 1
], voting='soft')
```

### 2.3 하이퍼파라미터 튜닝 ✅
**GridSearchCV 적용 (3-fold CV)**

| 모델 | 최적 파라미터 | CV ROC-AUC |
|------|--------------|------------|
| XGBoost | lr=0.05, depth=4, n=100 | 0.8491 |
| RandomForest | depth=6, n=200 | 0.8470 |
| GradientBoosting | lr=0.05, depth=3, n=100 | 0.8480 |

### 2.4 성능 개선 결과 ✅

| Metric | Baseline | Ensemble | 개선율 |
|--------|----------|----------|--------|
| **Accuracy** | 80.27% | **81.12%** | +1.06% |
| **Precision** | 66.44% | **69.15%** | +4.08% |
| **Recall** | 51.87% | **52.14%** | +0.52% |
| **F1-Score** | 58.26% | **59.45%** | +2.05% |
| **ROC-AUC** | 84.49% | **84.76%** | +0.31% |

### 2.5 API 문서화 강화 ✅
- OpenAPI 메타데이터 추가
- Pydantic 응답 모델 정의
- 엔드포인트별 상세 설명
- Swagger UI (`/docs`) 자동 생성

**새 API 기능:**
- `POST /api/predict` - 위험 요소 분석 + 맞춤 제안 반환
- `GET /api/stats` - 모델 메트릭스 포함
- `GET /api/analysis` - 세그먼트 분석 강화
- `GET /api/model-info` - 모델 메타데이터

---

## Phase 3: 운영 최적화 ✅

### 3.1 Rate Limiting ✅
- `limiter.py` - slowapi 적용
- 테스트 환경 자동 비활성화
- 엔드포인트별 제한: 20/분

### 3.2 로깅 시스템 ✅
- `logger.py` - RotatingFileHandler 적용
- 최대 파일 크기: 10MB
- 백업 파일: 5개 유지
- 콘솔 + 파일 동시 로깅

### 3.3 에러 핸들링 강화 ✅
- `exceptions.py` - 커스텀 예외 클래스
- `ChurnException` (기본 예외)
- `PredictionError` (예측 오류)
- `ModelLoadError` (모델 로드 실패)
- `DatabaseError` (DB 오류)
- 글로벌 예외 핸들러 적용

### 3.4 CI/CD 파이프라인 ✅
- `.github/workflows/ci.yml`
- Python 3.9 환경
- Push/PR 트리거 (main 브랜치)
- 자동 테스트 실행

---

## Phase 4: 고도화 🔄 (진행 중)

### 4.1 알림 시스템 ✅
- `ToastContext.jsx` - Toast 알림 컴포넌트
- 4가지 알림 타입: success, error, warning, info
- 애니메이션 효과 (framer-motion)
- 자동 소멸 (기본 4초)
- 예측 결과 기반 알림:
  - 위험 (>70%): 빨간색 에러 알림
  - 주의 (50-70%): 노란색 경고 알림
  - 안전 (<50%): 초록색 성공 알림

### 4.2 Predictor 폼 확장 ✅
- 기본 정보 6개 필드 (상시 표시)
- 고급 옵션 토글 (13개 추가 필드)
- 고객 정보: 성별, 시니어, 배우자, 부양가족
- 서비스 옵션: 전화, 인터넷 부가서비스 등

### 4.3 예측 결과 UI 개선 ✅
- 위험 요인 분석 표시 (risk_factors)
- 대응 전략 상세 정보 (action, priority, details, expected_impact)
- 신뢰도 및 모델 버전 표시

### TODO
- [ ] 모델 A/B 테스팅
- [ ] 실시간 대시보드 업데이트 (WebSocket)
- [ ] 이메일/슬랙 외부 알림 연동
- [ ] 고급 분석 리포트 PDF 내보내기

---

## 현재 아키텍처

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │     │    FastAPI      │     │  Spring Boot    │
│   React + Vite  │────▶│   (Python)      │     │    (Java)       │
│     :5174       │     │     :8002       │     │     :8001       │
└─────────────────┘     └────────┬────────┘     └────────┬────────┘
                               │                        │
                        ┌──────▼────────────────────────▼──────┐
                        │           PostgreSQL / SQLite        │
                        └──────────────────────────────────────┘
```

---

## 파일 구조

```
Churn-Guard-AI/
├── backend/
│   ├── main.py              # FastAPI 앱 (v2.0.0)
│   ├── auth.py              # JWT 인증
│   ├── database.py          # SQLAlchemy 설정
│   ├── db_models.py         # DB 모델
│   ├── models.py            # Pydantic 모델
│   ├── services.py          # v1 서비스
│   ├── services_v2.py       # v2 서비스 (Feature Engineering)
│   ├── limiter.py           # Rate Limiting (slowapi)
│   ├── logger.py            # 로깅 시스템
│   ├── exceptions.py        # 커스텀 예외 클래스
│   ├── train_model.py       # v1 모델 학습
│   ├── train_model_v2.py    # v2 앙상블 모델 학습
│   ├── churn_model_v2.pkl   # 앙상블 모델
│   ├── feature_names_v2.pkl # 특성 목록
│   ├── model_metadata_v2.json
│   ├── routers/
│   │   ├── auth.py
│   │   ├── prediction.py    # v1 라우터
│   │   └── prediction_v2.py # v2 라우터 (문서화 강화)
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_main.py
│   │   ├── test_auth.py
│   │   ├── test_prediction.py
│   │   └── test_integration.py
│   ├── logs/                # 로그 파일 디렉토리
│   └── data/
│       └── Customer-Churn.csv
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── AuthContext.jsx
│   │   ├── ToastContext.jsx    # Toast 알림 시스템
│   │   └── Login.jsx
│   ├── vite.config.js
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── Dockerfile.springboot
├── IMPROVEMENT_PLAN.md
└── PROGRESS.md              # 이 파일
```

---

## 실행 방법

### 로컬 개발
```bash
# Backend (FastAPI)
cd backend
python main.py  # :8002

# Frontend
cd frontend
npm run dev  # :5174

# Spring Boot
./gradlew bootRun  # :8001
```

### Docker
```bash
# 전체 실행
docker-compose up -d

# 프로덕션 (nginx 포함)
docker-compose --profile production up -d
```

### 테스트
```bash
cd backend
pytest tests/ -v
```

---

## 로그인 정보

| 항목 | 값 |
|------|-----|
| Username | admin |
| Password | admin123 |

---

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 헬스체크 |
| GET | `/docs` | Swagger UI |
| POST | `/api/token` | 로그인 |
| POST | `/api/predict` | 이탈 예측 |
| GET | `/api/stats` | 통계 조회 |
| GET | `/api/analysis` | 상세 분석 |
| GET | `/api/model-info` | 모델 정보 |

---

## 다음 단계

1. ~~**Phase 3 시작**~~ ✅ 완료
2. ~~**프론트엔드 v2 적용**~~ ✅ 완료 - 새 API 응답 형식 반영
3. **Phase 4 시작** - 모델 A/B 테스팅, WebSocket, 알림 시스템
4. **프로덕션 배포 준비** - Docker 테스트, 환경 분리
