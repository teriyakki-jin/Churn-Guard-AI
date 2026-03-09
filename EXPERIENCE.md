# ChurnGuard AI - 프로젝트 경험 정리

## 1. 프로젝트 목적

### 배경 및 문제 정의
통신사는 고객 이탈(Churn)이 발생한 후에 인지하는 경우가 대부분이다. 이미 떠난 고객을 되돌리는 비용은 신규 고객 유지 비용보다 5~7배 높다. 이 프로젝트는 **이탈이 발생하기 전에 고위험 고객을 식별하고, 맞춤 유지 전략을 자동으로 제안**하는 시스템을 목표로 했다.

### 해결하고자 한 것
- 고객 프로필 입력 시 이탈 확률(0~100%) 실시간 예측
- 이탈에 기여하는 주요 요인(Risk Factors) 자동 식별
- 고객 특성에 맞는 구체적 유지 전략 제안 (할인, 약정 변경 등)
- 실시간 시뮬레이션으로 모델 동작을 직관적으로 시각화

### 비즈니스 임팩트 (모델 기준)
| 지표 | 기존 | 개선 후 |
|------|------|---------|
| 이탈 방지율 | 20% | 35% |
| 고객 유지 비용 | $450 | $300 |
| ROI | $593 | $850 |

---

## 2. 적용 기술 (Techniques)

### 2-1. ML 모델: Voting Ensemble

**문제**: 단일 XGBoost 모델로 Accuracy 80%, ROC-AUC 0.84에 머물렀음.

**해결**: 세 모델의 약점을 상호 보완하는 Soft Voting Ensemble 구성.

```python
VotingClassifier([
    ('xgb', XGBClassifier()),      # 가중치: 2 (비선형 패턴에 강함)
    ('rf', RandomForestClassifier()),  # 가중치: 1 (과적합 방지)
    ('gb', GradientBoostingClassifier()) # 가중치: 1 (순차 오류 보정)
], voting='soft')  # 확률 평균으로 최종 예측
```

**결과**: Accuracy 81.1% (+1%), Precision 69.2% (+4%), ROC-AUC 0.8476 달성.

**XGBoost에 가중치 2를 준 이유**: GridSearchCV로 단일 모델 CV 성능 비교 시 XGBoost(0.8491)가 RF(0.8470), GB(0.8480)보다 일관되게 높았기 때문.

---

### 2-2. Feature Engineering: 도메인 지식 기반 특성 생성

원본 데이터 19개 컬럼에서 **10개 파생 특성**을 추가해 모델에 비즈니스 인사이트를 주입했다.

| 특성명 | 계산 로직 | 중요도 |
|--------|-----------|--------|
| `ContractStability` | 계약 유형 → 수치 매핑 (월납=1, 1년=2, 2년=3) | **22.6%** |
| `FiberNoSecurity` | 광섬유 인터넷 + 보안 서비스 미가입 플래그 | **14.2%** |
| `CustomerValueScore` | tenure×0.3 + 월정액비율×0.4 + 총청구비율×0.3 | - |
| `PaymentRisk` | 전자수표=3, 우편=2, 계좌이체/카드=1 | 1.6% |
| `TenureGroup` | 0-12개월/13-24/25-48/49-72 그룹화 | 2.2% |

**핵심 인사이트**: `ContractStability`가 1위를 차지했다. 이는 "월-to-월" 계약 고객이 장기 계약 대비 이탈 확률이 3배 이상 높다는 비즈니스 직관과 일치.

---

### 2-3. A/B Testing: 안전한 모델 교체 전략

프로덕션에서 새 모델을 검증하기 위해 트래픽 분리 전략을 구현했다.

```python
# TrafficRouter: weighted random selection
selected = random.choices(
    ['v2', 'v2_candidate'],
    weights=[0.8, 0.2],  # 80/20 분배
    k=1
)[0]
```

- **ModelRegistry**: 모델을 딕셔너리로 관리, ID 기반 조회
- **TrafficRouter**: 가중치 합이 1.0이 아닐 경우 자동 정규화
- 새 모델이 기존 성능 이상이면 weights를 100/0으로 전환

---

### 2-4. WebSocket 실시간 시뮬레이션

```
Client ──── WS Connect ────▶ FastAPI ConnectionManager
              ◀── streaming ── 가상 고객 생성 → 예측 → 브로드캐스트
```

- `/ws/simulation?interval=2.0&token=...` — JWT를 쿼리 파라미터로 받아 인증
- 0.5~10초 간격 조절 가능
- 연결 관리: `ConnectionManager` 클래스로 active connection 추적

---

### 2-5. 보안 레이어 (다층 방어)

| 레이어 | 구현 |
|--------|------|
| 인증 | JWT Bearer (python-jose), 60분 만료 |
| 계정 보호 | 5회 실패 → 5분 잠금 (메모리 기반 lockout 카운터) |
| 비밀번호 | bcrypt 해싱 + 복잡도 정책 (대/소/숫자/특수) |
| API 보호 | slowapi Rate Limiting (엔드포인트별 차등) |
| 전송 보안 | HTTP 보안 헤더 7종 (HSTS, CSP, X-Frame-Options 등) |
| 네트워크 | CORS 화이트리스트 |
| 시크릿 | .env 환경변수 분리 |

---

### 2-6. 아키텍처: 관심사 분리

```
backend/
├── main.py          # 미들웨어, 라우터 등록
├── routers/         # 도메인별 엔드포인트 분리
│   ├── auth.py      # 인증
│   ├── prediction_v2.py  # 예측
│   ├── simulation.py     # WebSocket
│   └── reports.py        # 리포트
├── services_v2.py   # 비즈니스 로직
├── db_models.py     # ORM (데이터 정의)
├── models.py        # Pydantic (입출력 검증)
└── exceptions.py    # 커스텀 예외 계층
```

FastAPI의 Dependency Injection으로 `get_current_user()`를 라우터마다 주입 — 인증 로직 중복 제거.

---

### 2-7. 통계 분석 적용

단순 집계가 아닌 **통계적 유의성 검정**으로 이탈 요인을 분석:

- **Chi-square test**: 범주형 변수 (계약 유형, 결제 방법)와 이탈 간 연관성 검정
- **Mann-Whitney U test**: 연속형 변수 (tenure, 월정액)의 이탈/비이탈 그룹 분포 차이 검정

---

## 3. 트러블슈팅

### 3-1. 시크릿 키 하드코딩

**발생**: 초기 버전 `auth.py`에 `SECRET_KEY = "supersecretkey"` 하드코딩.

**문제점**: git push 시 시크릿 노출, 환경별 분리 불가.

**해결**:
```python
# Before
SECRET_KEY = "supersecretkey"

# After
from dotenv import load_dotenv
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not configured")
```
`env.example` 템플릿 제공 + `.gitignore`에 `.env` 추가.

---

### 3-2. Rate Limit이 테스트를 막는 문제

**발생**: pytest 실행 시 `/api/token` 5/min 제한에 걸려 인증 테스트 전체 실패.

**원인**: slowapi가 테스트 환경 구분 없이 실제 IP로 제한 적용.

**해결**: `conftest.py`에서 앱 시작 전 limiter를 mock으로 교체.
```python
# conftest.py
@pytest.fixture
def client():
    app.state.limiter = MagicMock()  # Rate limit 비활성화
    with TestClient(app) as c:
        yield c
```

---

### 3-3. WebSocket JWT 인증 방식

**발생**: WebSocket은 HTTP Header를 지원하지 않아 Bearer 토큰 전달 불가.

**해결**: 쿼리 파라미터로 토큰 수신 후 서버에서 즉시 검증.
```
ws://localhost:8000/api/ws/simulation?token=eyJ...
```
연결 수립 직후 토큰 유효성 검사 → 실패 시 즉시 연결 종료.

**보안 고려**: HTTPS(WSS) 환경에서는 쿼리 파라미터도 암호화되므로 허용 가능한 방식.

---

### 3-4. Feature Engineering 데이터 누수 (Data Leakage)

**발생**: `CustomerValueScore` 계산 시 `TotalCharges`의 최댓값을 테스트 데이터 포함 전체에서 가져옴.

**원인**: 정규화 기준(max값)을 학습 데이터가 아닌 전체 데이터셋에서 계산.

**해결**: 정규화 기준을 학습 CSV(`Customer-Churn.csv`)에서만 계산하도록 고정.
```python
ref_df = pd.read_csv('data/Customer-Churn.csv')  # 학습 데이터 기준
max_charges = ref_df['MonthlyCharges'].max()      # 고정 기준값 사용
```

---

### 3-5. 앙상블 모델 확률 불일치

**발생**: Soft Voting 시 XGBoost의 predict_proba가 0.0 또는 1.0 극단값을 자주 반환.

**원인**: XGBoost 기본 설정에서 `eval_metric` 미지정 시 확률 보정 불완전.

**해결**: `use_label_encoder=False`, `eval_metric='logloss'` 명시 + `probability=True` soft voting으로 세 모델 확률의 가중 평균 사용.

---

### 3-6. Docker Compose 서비스 시작 순서

**발생**: FastAPI 컨테이너가 PostgreSQL보다 먼저 시작되어 DB 연결 오류 발생.

**해결**: `depends_on` + `healthcheck` 조합.
```yaml
backend:
  depends_on:
    db:
      condition: service_healthy
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    retries: 5
```

---

### 3-7. PDF 생성 한글 폰트 깨짐

**발생**: `fpdf2`로 PDF 생성 시 한글 문자가 '□□□'으로 렌더링.

**원인**: fpdf2 기본 폰트(Helvetica)가 유니코드 미지원.

**해결**: 시스템 폰트 또는 내장 폰트를 명시적으로 등록.
```python
pdf.add_font('NanumGothic', '', 'fonts/NanumGothic.ttf', uni=True)
pdf.set_font('NanumGothic', size=12)
```

---

## 4. 개발 단계별 학습

| Phase | 핵심 학습 |
|-------|-----------|
| Phase 1 | 환경 분리(.env), ORM 설계, Docker 멀티스테이지 빌드 |
| Phase 2 | Feature Engineering, GridSearchCV, Ensemble 가중치 튜닝 |
| Phase 3 | Rate Limiting 설계, RotatingFileHandler, CI/CD 파이프라인 |
| Phase 4 | WebSocket 인증, A/B 테스팅 아키텍처, Toast UX 패턴 |

---

## 5. 아쉬운 점 / 다음에 개선할 것

- **모델 재학습 파이프라인 부재**: 신규 데이터 유입 시 수동으로 재학습 필요 → MLflow나 Airflow로 자동화 필요
- **Frontend 상태 관리**: App.jsx 단일 파일이 46KB — Zustand 도입으로 컴포넌트 분리 필요
- **A/B 테스트 결과 추적**: 현재 어느 모델로 예측했는지 DB에 저장되지 않아 성능 비교 불가
- **실시간 대시보드**: 시뮬레이션 결과가 대시보드에 자동 반영되지 않음 (수동 새로고침 필요)
