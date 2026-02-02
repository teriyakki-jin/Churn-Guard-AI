# ChurnGuard AI - 고객 이탈 예측 및 분석 시스템

**ChurnGuard AI**는 통신사 고객 데이터를 분석하여 이탈 위험을 예측하고, 데이터 기반의 유지(Retention) 전략을 제안하는 엔터프라이즈급 웹 애플리케이션입니다.

XGBoost 기반의 머신러닝 모델과 현대적인 React 프론트엔드, 그리고 운영 최적화가 적용된 FastAPI 백엔드를 통합하여 안정적이고 확장 가능한 서비스를 제공합니다.

## 🚀 주요 기능 (Key Features)

### 1. 📊 대시보드 및 분석 (Analytics)
- **실시간 대시보드**: 총 고객 수, 이탈률, 주요 지표를 한눈에 파악.
- **전략 분석**: 통계적 기법(Chi-square, Mann-Whitney U)을 활용한 심층 이탈 원인 분석.
- **데이터 시각화**: 계약 형태, 결제 방식 등에 따른 이탈 패턴을 직관적인 차트로 제공.

### 2. 🤖 AI 이탈 예측 (Prediction)
- **개별 위험도 예측**: 고객 프로필 입력 시 실시간으로 이탈 확률(0~100%) 계산.
- **위험 요인 식별**: 이탈에 기여하는 주요 요인(Risk Factors)을 분석하여 제시.
- **맞춤형 제안**: 고객 특성에 맞는 구체적인 유지 전략(할인, 약정 변경 등) 자동 생성.

### 3. 🛡️ 운영 최적화 (Operational Excellence) [New]
- **보안 및 트래픽 관리**: `slowapi`를 이용한 IP 기반 API 속도 제한 (Rate Limiting) 적용.
- **중앙 집중식 로깅**: `RotatingFileHandler`를 통한 요청/응답 및 에러 로그 체계적 관리.
- **향상된 에러 처리**: 표준화된 JSON 에러 응답 및 커스텀 예외 처리로 클라이언트 호환성 강화.
- **CI/CD 파이프라인**: GitHub Actions를 통한 자동화된 테스트 및 빌드 검증.

## 🛠️ 기술 스택 (Tech Stack)

| 영역 | 기술 |
|------|------|
| **Frontend** | React, Vite, Framer Motion, Recharts, Tailwind CSS (option) |
| **Backend (AI)** | FastAPI, Python 3.9+, Pandas, Scikit-learn, XGBoost |
| **Backend (Data)** | Spring Boot, Java 17, H2 Database (JPA) |
| **Database** | H2 (In-memory), SQLite (Test) |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **Testing** | Pytest, TestClient |

## 📂 프로젝트 구조 (Project Structure)

```
Churn-Guard-AI/
├── backend/                # FastAPI AI 서버
│   ├── routers/            # API 라우터 (auth, prediction)
│   ├── tests/              # Pytest 테스트 코드
│   ├── logs/               # 애플리케이션 로그
│   ├── models.py           # Pydantic 데이터 모델
│   ├── services_v2.py      # 비즈니스 로직 및 ML 서비스
│   ├── main.py             # 앱 진입점 및 설정
│   └── requirements.txt    # Python 의존성
├── frontend/               # React 웹 애플리케이션
├── docker-compose.yml      # 컨테이너 오케스트레이션 설정
├── .github/workflows/      # CI/CD 설정
└── README.md               # 프로젝트 문서
```

## 📦 시작하기 (Getting Started)

### 사전 요구 사항
- Docker Desktop (권장)
- Python 3.9+ (로컬 실행 시)
- Node.js 16+ (로컬 실행 시)

### 방법 1: Docker로 실행 (권장)

가장 간편하게 전체 서비스를 실행할 수 있습니다.

```bash
# 프로젝트 클론
git clone https://github.com/teriyakki-jin/Churn-Guard-AI.git
cd Churn-Guard-AI

# Docker Compose 실행
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 방법 2: 로컬에서 실행

#### Backend (Python)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## 🧪 테스트 실행 (Testing)

프로젝트의 안정성을 검증하기 위해 단위 및 통합 테스트를 실행할 수 있습니다.

```bash
cd backend

# 전체 테스트 실행
pytest tests/

# 상세 로그와 함께 실행
pytest tests/ -vv
```
*참고: 테스트 실행 시 Rate Limit은 자동으로 비활성화됩니다.*

## 🔒 라이센스 (License)

이 프로젝트는 MIT 라이센스 하에 배포됩니다.
