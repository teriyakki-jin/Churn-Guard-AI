# ChurnGuard AI - 고객 이탈 예측 및 분석 시스템

**ChurnGuard AI**는 통신사 고객 데이터를 분석하여 이탈 위험을 예측하고, 데이터 기반의 유지(Retention) 전략을 제안하는 엔터프라이즈급 웹 애플리케이션입니다.

Voting Ensemble (XGBoost + RandomForest + GradientBoosting) 기반의 머신러닝 모델과 현대적인 React 프론트엔드, 그리고 보안이 강화된 FastAPI 백엔드를 통합하여 안정적이고 확장 가능한 서비스를 제공합니다.

## 주요 기능 (Key Features)

### 1. 대시보드 및 분석 (Analytics)
- **실시간 대시보드**: 총 고객 수, 이탈률, 주요 지표를 한눈에 파악
- **전략 분석**: 통계적 기법(Chi-square, Mann-Whitney U)을 활용한 심층 이탈 원인 분석
- **데이터 시각화**: 계약 형태, 결제 방식 등에 따른 이탈 패턴을 직관적인 차트로 제공

### 2. AI 이탈 예측 (Prediction)
- **개별 위험도 예측**: 고객 프로필 입력 시 실시간으로 이탈 확률(0~100%) 계산
- **위험 요인 식별**: 이탈에 기여하는 주요 요인(Risk Factors)을 분석하여 제시
- **맞춤형 제안**: 고객 특성에 맞는 구체적인 유지 전략(할인, 약정 변경 등) 자동 생성

### 3. 실시간 시뮬레이션 (Simulation)
- **WebSocket 스트리밍**: 가상 고객을 실시간으로 생성하고 이탈 예측 수행
- **A/B 테스트 라우팅**: 트래픽을 v2(80%)와 v2_candidate(20%)로 분배하여 모델 성능 비교
- **라이브 시각화**: 예측 결과가 스트리밍되며 대시보드에서 실시간 확인 가능

### 4. 리포트 및 알림 (Reports & Notifications)
- **CSV/PDF 내보내기**: 분석 결과를 CSV 또는 PDF 형식으로 다운로드
- **이메일 리포트**: 분석 리포트를 이메일로 자동 발송
- **재무 영향 분석**: 이탈 방지 전략의 ROI 계산 포함

### 5. 보안 및 운영 (Security & Operations)
- **JWT 인증**: OAuth2 Bearer 토큰 기반 인증 시스템
- **계정 잠금**: 5회 로그인 실패 시 5분간 계정 잠금
- **비밀번호 정책**: 8자 이상, 대소문자/숫자/특수문자 필수
- **API 속도 제한**: `slowapi` 기반 엔드포인트별 Rate Limiting
- **HTTP 보안 헤더**: X-Frame-Options, CSP, HSTS 등 7종 적용
- **CORS 화이트리스트**: 허용된 Origin만 접근 가능
- **중앙 집중식 로깅**: `RotatingFileHandler` 기반 보안 이벤트 추적
- **CI/CD 파이프라인**: GitHub Actions 자동화된 테스트 및 빌드

## 기술 스택 (Tech Stack)

| 영역 | 기술 |
|------|------|
| **Frontend** | React 19, Vite 7, Framer Motion, Recharts, Lucide Icons |
| **Backend** | FastAPI, Python 3.9+, Pydantic v2, SQLAlchemy |
| **ML Model** | Voting Ensemble (XGBoost + RandomForest + GradientBoosting) |
| **Auth** | JWT (python-jose), bcrypt, OAuth2 Bearer |
| **Database** | SQLite (Dev), PostgreSQL (Prod) |
| **DevOps** | Docker, Docker Compose, GitHub Actions, Nginx |
| **Testing** | Pytest (30 tests), FastAPI TestClient |

## 프로젝트 구조 (Project Structure)

```
Churn-Guard-AI/
├── backend/
│   ├── routers/
│   │   ├── auth.py             # 인증 (로그인/회원가입/계정잠금)
│   │   ├── prediction_v2.py    # 이탈 예측 API
│   │   ├── simulation.py       # WebSocket 실시간 시뮬레이션
│   │   ├── reports.py          # CSV/PDF 리포트 생성
│   │   └── notifications.py    # 이메일 알림 발송
│   ├── tests/                  # Pytest 테스트 (30개)
│   ├── auth.py                 # JWT 토큰 관리
│   ├── models.py               # Pydantic 입력 검증 모델
│   ├── services_v2.py          # ML 예측 서비스
│   ├── ab_testing.py           # A/B 테스트 라우터
│   ├── simulation.py           # 시뮬레이션 엔진
│   ├── main.py                 # 앱 진입점 및 미들웨어
│   └── requirements.txt        # Python 의존성
├── frontend/
│   └── src/
│       ├── App.jsx             # 메인 앱 (대시보드/예측/전략)
│       ├── Login.jsx           # 로그인/회원가입 페이지
│       ├── Simulation.jsx      # 실시간 시뮬레이션 페이지
│       ├── AuthContext.jsx      # 인증 상태 관리
│       └── ToastContext.jsx     # 토스트 알림 컨텍스트
├── docker-compose.yml          # 컨테이너 오케스트레이션
├── env.example                 # 환경변수 템플릿
├── .github/workflows/          # CI/CD 설정
└── README.md
```

## 시작하기 (Getting Started)

### 사전 요구 사항
- Docker Desktop (권장)
- Python 3.9+ (로컬 실행 시)
- Node.js 16+ (로컬 실행 시)

### 방법 1: Docker로 실행 (권장)

```bash
# 프로젝트 클론
git clone https://github.com/teriyakki-jin/Churn-Guard-AI.git
cd Churn-Guard-AI

# 환경변수 설정
cp env.example .env
# .env 파일에서 SECRET_KEY, DB 설정 등 수정

# Docker Compose 실행
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8002`
- API Docs: `http://localhost:8002/docs`

### 방법 2: 로컬에서 실행

#### Backend (Python)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 환경변수 설정
export SECRET_KEY="your-secret-key"  # 필수

uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

#### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## API 엔드포인트 (API Endpoints)

| Method | Endpoint | 설명 | 인증 |
|--------|----------|------|------|
| `POST` | `/api/token` | 로그인 (JWT 발급) | - |
| `POST` | `/api/register` | 회원가입 | - |
| `POST` | `/api/predict` | 고객 이탈 예측 | Bearer |
| `GET` | `/api/stats` | 전체 통계 조회 | Bearer |
| `GET` | `/api/analysis` | 심층 분석 데이터 | Bearer |
| `GET` | `/api/model/info` | 모델 메타데이터 | Bearer |
| `GET` | `/api/reports/export/csv` | CSV 리포트 다운로드 | Bearer |
| `GET` | `/api/reports/export/pdf` | PDF 리포트 다운로드 | Bearer |
| `POST` | `/api/notifications/send-report` | 이메일 리포트 발송 | Bearer |
| `WS` | `/api/ws/simulation` | 실시간 시뮬레이션 | Token (query) |

## 테스트 실행 (Testing)

```bash
cd backend

# 전체 테스트 실행 (30개)
pytest tests/ -v

# 커버리지 포함
pytest tests/ -v --tb=short
```

*참고: 테스트 실행 시 Rate Limit은 자동으로 비활성화됩니다.*

## ML 모델 성능

| 지표 | 값 |
|------|-----|
| **Type** | Voting Ensemble (XGBoost + RF + GBM) |
| **Accuracy** | ~84% |
| **ROC-AUC** | 0.88 |
| **Features** | 50+ engineered features |

## 라이센스 (License)

이 프로젝트는 MIT 라이센스 하에 배포됩니다.
