# ChurnGuard AI — 프로젝트 회고

> 개발 기간: 2025.01 ~ 2026.03
> 역할: 풀스택 개발 (ML · Backend · Frontend · DevOps) 1인
> GitHub: https://github.com/teriyakki-jin/Churn-Guard-AI

---

## 1. 왜 만들었나

통신사 도메인에서 고객 이탈은 **이미 일어난 뒤에 인지**하는 경우가 대부분이다.
떠난 고객을 되돌리는 비용은 기존 고객 유지의 5~7배. 즉, 이탈을 **예측하고 선제 대응**하는 것이 핵심이다.

이 프로젝트의 목표:
1. 고객 프로필 입력 시 이탈 확률(0~100%) 실시간 예측
2. 이탈을 유발하는 주요 요인(Risk Factors) 자동 분석
3. 고객 특성에 맞는 유지 전략(할인, 계약 변경 등) 자동 제안
4. 실시간 시뮬레이션으로 모델 동작을 직관적으로 시각화

단순한 예측 API가 아니라 **비즈니스 의사결정까지 연결되는 시스템**을 목표로 했다.

---

## 2. 기술적 의사결정과 그 이유

### 2-1. Voting Ensemble — 왜 단일 모델을 쓰지 않았나

초기에는 XGBoost 단일 모델로 Accuracy 80%, ROC-AUC 0.84에서 시작했다.
문제는 특정 세그먼트(단기 고객, 고액 요금제)에서 예측이 불안정했던 것.

세 모델의 약점을 상호 보완하는 **Soft Voting Ensemble**을 구성했다:

```python
VotingClassifier([
    ('xgb', XGBClassifier()),           # 가중치 2 — 비선형 패턴에 강함
    ('rf', RandomForestClassifier()),   # 가중치 1 — 과적합 방지
    ('gb', GradientBoostingClassifier()) # 가중치 1 — 순차 오류 보정
], voting='soft')
```

XGBoost에 가중치 2를 준 이유: GridSearchCV 교차검증에서 XGBoost(0.8491)가 RF(0.8470), GB(0.8480)보다 일관되게 높았기 때문이다.

**결과**: Accuracy 81.1%, Precision 69.2%, ROC-AUC 0.8476 — 단일 모델 대비 안정성 향상.

---

### 2-2. Feature Engineering — 도메인 지식을 모델에 주입

원본 19개 컬럼에서 **10개 파생 피처**를 추가했다.
단순 숫자를 넣는 게 아니라 비즈니스 인사이트를 모델 입력으로 변환하는 과정이었다.

| 피처명 | 의미 | 중요도 |
|--------|------|--------|
| `ContractStability` | 계약 유형을 안정성 점수로 매핑 (월납=1, 1년=2, 2년=3) | **22.6%** |
| `FiberNoSecurity` | 광섬유 + 보안 미가입 고위험 플래그 | **14.2%** |
| `CustomerValueScore` | tenure·월정액·총청구액 가중 합산 | - |
| `PaymentRisk` | 결제 수단별 이탈 위험 점수 | 1.6% |
| `TenureGroup` | 가입 기간을 4구간으로 범주화 | 2.2% |

`ContractStability`가 1위를 차지한 건 비즈니스 직관과 정확히 일치한다.
"월-to-월 계약 고객은 2년 계약보다 14배 높은 이탈률"이라는 통계가 모델에도 반영된 것.

---

### 2-3. A/B 테스팅 아키텍처 — 프로덕션에서 모델을 안전하게 교체하는 법

새 모델을 바로 100% 배포하는 건 위험하다. 그래서 **트래픽 분리** 전략을 구현했다.

```python
# TrafficRouter: 80/20 가중치 랜덤 분배
selected = random.choices(
    ['v2', 'v2_candidate'],
    weights=[0.8, 0.2],
    k=1
)[0]
```

- `ModelRegistry`: 모델을 딕셔너리로 관리, ID 기반 hot-swap 가능
- `TrafficRouter`: 가중치 합이 1.0이 아닐 경우 자동 정규화
- 각 예측 결과에 `model_version` 기록 → DB에서 성능 비교 가능

이 구조 덕분에 새 모델 성능이 검증되면 weights를 [1.0, 0.0]으로 바꾸는 것만으로 교체 완료.

---

### 2-4. 보안 설계 — 단순 JWT 이상으로

API 보안을 레이어별로 쌓았다:

| 레이어 | 구현 |
|--------|------|
| 인증 | JWT Bearer (python-jose), 60분 만료 |
| 계정 보호 | 5회 실패 → 5분 잠금 (메모리 lockout 카운터) |
| 비밀번호 | bcrypt 해싱 + 복잡도 정책 (대/소/숫자/특수) |
| API 보호 | slowapi — 엔드포인트별 차등 Rate Limiting |
| 전송 보안 | HTTP 보안 헤더 7종 (HSTS, CSP, X-Frame-Options 등) |
| 네트워크 | CORS 화이트리스트 |
| 시크릿 | .env 환경변수 분리, SECRET_KEY 미설정 시 즉시 에러 |

처음에 `SECRET_KEY = "supersecretkey"` 하드코딩했다가 git push 직전에 잡았다. 이후 `.env` + `.gitignore` 체계로 전환.

---

### 2-5. WebSocket 실시간 시뮬레이션

WebSocket은 HTTP 헤더를 지원하지 않아 Bearer 토큰 전달이 불가능하다.
쿼리 파라미터로 JWT를 받아 연결 즉시 검증하는 방식으로 해결했다:

```
ws://localhost:8000/api/ws/simulation?token=eyJ...&interval=2.0
```

- 연결 수립 직후 토큰 유효성 검사 → 실패 시 즉시 연결 종료
- `ConnectionManager`로 active connection 목록 관리
- 0.5~10초 간격 조절로 실시간성 체험 가능

HTTPS(WSS) 환경에서는 쿼리 파라미터도 암호화되므로 보안상 허용 가능한 방식이다.

---

### 2-6. 아키텍처 — 관심사 분리

FastAPI의 Dependency Injection을 활용해 인증·DB·서비스를 레이어로 분리했다:

```
main.py           → 미들웨어, 라우터 등록
routers/          → 도메인별 엔드포인트 (auth / prediction / simulation / reports)
services_v2.py    → 비즈니스 로직 (예측, 피처 엔지니어링)
db_models.py      → ORM 모델 (데이터 구조 정의)
models.py         → Pydantic 스키마 (입출력 검증)
exceptions.py     → 커스텀 예외 계층
service_container.py → DI 컨테이너
```

`get_current_user()`를 Depends로 주입해 인증 로직 중복을 제거했다.
초반에 라우터마다 토큰 검증 코드를 복붙했는데, 이걸 한 번에 정리한 게 가장 큰 코드 품질 개선이었다.

---

## 3. 트러블슈팅

### 3-1. CI 전체 실패 — bcrypt 버전 충돌

**현상**: 로컬에서는 30개 테스트 전부 통과하는데, GitHub Actions CI에서만 7개 FAILED.

**에러 메시지**:
```
ValueError: password cannot be longer than 72 bytes, truncate manually
```

**원인 추적**: 로컬 bcrypt 버전은 3.2.0, CI는 버전 미핀으로 최신(4.x) 설치.
bcrypt 4.0부터 72바이트 초과 시 에러로 처리하는데, passlib 1.7.4가 내부 헬스체크에서 긴 문자열을 bcrypt에 전달해 충돌 발생.

**해결**: `requirements.txt`에 `bcrypt<4.0.0` 핀 추가.
**교훈**: 의존성 버전은 항상 핀하거나 range로 제한해야 한다. CI 환경이 로컬과 다를 수 있다는 걸 이 이슈로 체득했다.

---

### 3-2. notifications.py — 이메일이 조용히 실패하는 버그

**현상**: `/notifications/send-report` API는 200을 반환하는데 실제로 이메일이 안 감. 로그에는:
```
ERROR - Error sending report email: object NoneType can't be used in 'await' expression
```

**원인 추적**: 두 단계 문제였다.
1. 테스트에서 FastMail을 `MagicMock`으로 스터빙 → `send_message()` 반환값이 coroutine이 아닌 MagicMock → `await MagicMock` 실패
2. 실패가 `except` 블록에서 묻혀서 API는 200을 반환 → 조용한 실패

**해결**:
- 테스트: `send_message`를 `AsyncMock`으로 교체
- 프로덕션: coroutine 여부 체크 후 await + 에러 로그에 타입 정보 추가

**교훈**: `try/except`가 너무 넓으면 실패가 숨는다. 배경 작업은 결과를 확인할 방법을 별도로 만들어야 한다.

---

### 3-3. Feature Mismatch — 모델과 피처가 맞지 않는 문제

**현상**: v2 모델 교체 후 예측 API에서 400 에러 발생.

**에러**:
```
feature_names mismatch: training data did not have the following fields:
ContractStability, AvgMonthlySpend, CustomerValueScore ...
```

**원인**: `churn_model.pkl`은 피처 엔지니어링 전 45개 피처로 학습됐는데, `feature_names_v2.pkl`은 엔지니어링 포함 57개 피처 목록을 담고 있었다.

**해결**: `feature_names_v2.pkl`도 v1(45개) 기준으로 교체.
`services_v2.py`가 `feature_names`를 기준으로 컬럼 선택(`final_df[self.feature_names]`)하는 구조였기 때문에 pkl 교체만으로 해결됐다.

**교훈**: 모델 파일과 피처 목록 파일은 항상 쌍으로 관리해야 한다. 모델 교체 시 피처 명세도 함께 갱신하는 체크리스트가 필요하다.

---

### 3-4. Rate Limiting이 테스트를 막는 문제

**발생**: pytest 실행 시 `/api/token` 5/min 제한에 걸려 인증 테스트 전체 실패.

**원인**: slowapi가 테스트 환경 구분 없이 실제 IP로 제한 적용.

**해결**: `conftest.py`에서 limiter 비활성화.
```python
limiter.enabled = False
```

---

### 3-5. XGBoost 확률 극단값 문제

**발생**: Soft Voting 시 XGBoost의 `predict_proba`가 0.0 또는 1.0 극단값을 자주 반환.

**원인**: `eval_metric` 미지정 시 확률 보정이 불완전.

**해결**: `use_label_encoder=False`, `eval_metric='logloss'` 명시 + soft voting으로 세 모델 확률의 가중 평균 사용.

---

### 3-6. Data Leakage — 학습 데이터 오염

**발생**: `CustomerValueScore` 계산 시 정규화 기준(max값)을 전체 데이터에서 가져옴.

**원인**: 테스트 데이터의 정보가 학습 과정에 유입되는 데이터 누수.

**해결**: 정규화 기준을 학습 CSV에서만 계산하도록 고정.
```python
ref_df = pd.read_csv('data/Customer-Churn.csv')
max_charges = ref_df['MonthlyCharges'].max()  # 학습 데이터 기준으로 고정
```

---

### 3-7. Docker Compose 서비스 시작 순서

**발생**: FastAPI 컨테이너가 PostgreSQL보다 먼저 시작되어 DB 연결 오류.

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

## 4. 단계별 성장

| Phase | 주요 작업 | 핵심 학습 |
|-------|-----------|-----------|
| Phase 1 | API 기초, 인증, DB 설계 | ORM 레이어 분리, .env 보안, Docker 멀티스테이지 빌드 |
| Phase 2 | ML 파이프라인, Feature Engineering | GridSearchCV, Ensemble 가중치 튜닝, Data Leakage 방지 |
| Phase 3 | 보안 강화, 로깅, CI/CD | Rate Limiting 설계, RotatingFileHandler, GitHub Actions |
| Phase 4 | WebSocket, A/B Testing, 리포트 | 실시간 스트리밍, 트래픽 분리, PDF 생성 |
| Phase 5 | 버그 수정, 리팩토링 | 의존성 버전 관리, 컴포넌트 분리, 조용한 실패 방지 |

---

## 5. 아쉬운 점과 다음 과제

### 해결한 것 (이번 세션에서)
- ~~A/B 결과 DB에 미저장~~ → `PredictionHistory.model_version` 기록 완료
- ~~App.jsx 46KB 모놀리스~~ → 5개 컴포넌트로 분리 (960줄 → 60줄)
- ~~notifications async 버그~~ → AsyncMock + coroutine 체크 수정

### 남은 과제
| 과제 | 이유 | 우선순위 |
|------|------|----------|
| 모델 재학습 파이프라인 | 신규 데이터 반영이 수동 | 높음 |
| 프론트 커스텀 훅 분리 | API 호출이 컴포넌트 내부에 산재 | 중간 |
| 테스트 커버리지 80% | 현재 60%, E2E 없음 | 중간 |
| 구조화 로깅 (JSON) | 현재 텍스트 로그는 집계 불가 | 낮음 |
| 실시간 대시보드 갱신 | 시뮬레이션 결과 수동 새로고침 | 낮음 |

---

## 6. 이 프로젝트에서 얻은 것

**ML과 프로덕션의 차이**
모델 정확도보다 모델을 안전하게 교체하고, 예측 결과를 추적하고, 실패를 감지하는 구조가 더 중요하다는 걸 느꼈다.

**"조용한 실패"의 위험성**
notifications 버그처럼 API가 200을 반환하면서 실제로는 아무것도 안 하는 경우가 가장 찾기 어렵다. 배경 작업은 반드시 결과를 관측할 수 있어야 한다.

**의존성 관리의 중요성**
bcrypt CI 버그처럼 버전 미핀은 로컬과 CI가 달라지는 근본 원인이다. 모든 의존성은 버전을 명시하거나 허용 범위를 제한해야 한다.

**1인 풀스택의 한계와 강점**
ML → API → 프론트 → 배포까지 전체 흐름을 혼자 설계하면서, 각 레이어가 서로 어떻게 맞물리는지 깊이 이해할 수 있었다. 반면 각 영역의 깊이는 전문팀보다 얕을 수밖에 없다. 그 간극을 메우는 게 다음 목표다.
