# ChurnGuard AI

[![CI](https://github.com/teriyakki-jin/Churn-Guard-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/teriyakki-jin/Churn-Guard-AI/actions/workflows/ci.yml)

![Python](https://img.shields.io/badge/Python-3.9-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-FF6600?logo=xgboost&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?logo=jsonwebtokens&logoColor=white)

통신사 고객 데이터를 기반으로 이탈 위험을 예측하고, 데이터 기반 유지 전략을 제안하는 엔터프라이즈급 웹 애플리케이션입니다.

## 1. 문제 정의
고객 이탈은 기업의 매출과 LTV에 직접적인 영향을 줍니다. 본 프로젝트는 이탈 고위험 고객을 조기에 식별하고, 우선 대응 전략을 제시하는 것을 목표로 합니다.

## 2. 접근 방법
- **Voting Ensemble** (XGBoost×2 + RandomForest×1 + GradientBoosting×1, soft voting)으로 예측 안정성 확보
- 예측 결과와 함께 위험 요인(Risk Factors) 및 맞춤형 대응 전략 자동 제공
- **A/B 테스트 라우팅** (v2 80% / candidate 20%)으로 운영 중 모델 비교 검증
- **WebSocket 실시간 시뮬레이션**으로 스트리밍 예측 지원

## 3. 주요 기능
| 기능 | 설명 |
|------|------|
| 실시간 KPI 대시보드 | 전체 이탈률, 고위험 고객 수, 수익 영향 시각화 |
| 이탈 확률 예측 | 개별 고객 이탈 확률 0~100% 산출 |
| 위험 요인 분석 | 상위 기여 피처 및 SHAP 기반 설명 |
| 맞춤형 유지 전략 | 계약 유형, 결제 방식별 자동 제안 |
| 실시간 시뮬레이션 | WebSocket 스트리밍 배치 예측 |
| A/B 모델 비교 | 운영 중 신규 모델 성능 검증 |
| 리포트 내보내기 | CSV / PDF 다운로드 및 이메일 발송 |
| 보안 | JWT 인증, 5회 실패 시 5분 잠금, 분당 요청 제한 |

## 4. 모델 성능
- **정확도**: ~84%
- **ROC-AUC**: 0.88
- **주요 피처**: ContractStability (22.6%), FiberNoSecurity (14.2%), CustomerValueScore
- **피처 수**: ~50개 (엔지니어링 포함)

## 5. 기술 스택
| 영역 | 기술 |
|------|------|
| Frontend | React 19.2, Vite 7.2, Recharts, Framer Motion, Axios |
| Backend | FastAPI, SQLAlchemy, Pydantic, slowapi |
| ML | XGBoost, RandomForest, GradientBoosting, scikit-learn |
| Auth | JWT (python-jose), bcrypt, OAuth2 Bearer |
| Database | SQLite (개발) / PostgreSQL (운영) |
| Infra | Docker, Docker Compose, Nginx |
| CI/CD | GitHub Actions (pytest, ESLint, Docker build) |

## 6. 시스템 아키텍처

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/c795e065-b26a-4d42-89e1-6bf87999e974" />


## 7. 프로젝트 구조
```text
Churn-Guard-AI/
├── backend/
│   ├── main.py                 # FastAPI 앱, 미들웨어, CORS
│   ├── services_v2.py          # ChurnServiceV2, 피처 엔지니어링, 예측
│   ├── ab_testing.py           # A/B 라우터, ModelRegistry
│   ├── auth.py                 # JWT 생성/검증, 비밀번호 해싱
│   ├── routers/
│   │   ├── prediction_v2.py    # /predict, /stats, /analysis, /model-info
│   │   ├── simulation.py       # WebSocket /ws/simulation, batch
│   │   ├── reports.py          # CSV/PDF 내보내기
│   │   └── notifications.py    # 이메일 알림
│   ├── tests/                  # pytest (30+ 테스트)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx             # 메인 대시보드
│       ├── Simulation.jsx      # WebSocket 시뮬레이션 UI
│       ├── Login.jsx           # 인증 UI
│       └── AuthContext.jsx     # 인증 상태 관리
├── nginx/                      # 리버스 프록시 설정
├── .github/workflows/ci.yml    # CI/CD 파이프라인
├── docker-compose.yml
└── env.example
```

## 8. 실행 방법

### Docker (권장)
```bash
git clone https://github.com/teriyakki-jin/Churn-Guard-AI.git
cd Churn-Guard-AI
cp env.example .env
# .env의 SECRET_KEY를 안전한 값으로 변경
docker-compose up --build
```

### 로컬 개발
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8002

# Frontend (별도 터미널)
cd frontend
npm install
npm run dev
```

## 9. 환경 변수
| 변수 | 설명 | 기본값 |
|------|------|--------|
| `SECRET_KEY` | JWT 서명 키 (필수 변경) | - |
| `ALGORITHM` | JWT 알고리즘 | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 시간 | 60 |
| `DATABASE_URL` | DB 연결 문자열 | sqlite:///./churn_guard.db |
| `CORS_ALLOW_ORIGINS` | 허용 출처 (콤마 구분) | http://localhost:5173 |

## 10. API 엔드포인트
| 메서드 | 경로 | 설명 | 제한 |
|--------|------|------|------|
| POST | `/api/token` | 로그인 | 5/min |
| POST | `/api/register` | 회원가입 | 3/min |
| POST | `/api/predict` | 이탈 예측 | 20/min |
| GET | `/api/stats` | 통계 조회 | - |
| GET | `/api/analysis` | 원인 분석 | - |
| GET | `/api/model-info` | 모델 정보 | - |
| WS | `/api/ws/simulation` | 실시간 스트리밍 | - |
| GET | `/api/simulation/batch` | 배치 예측 | - |
| GET | `/api/reports/export/csv` | CSV 내보내기 | 10/hour |
| GET | `/api/reports/export/pdf` | PDF 내보내기 | 10/hour |

## 11. 서비스 주소
- Frontend: http://localhost:5173
- Backend API: http://localhost:8002
- API Docs (Swagger): http://localhost:8002/docs

## 12. 테스트
```bash
cd backend
pytest tests/ -v --cov=. --cov-report=term-missing
```
현재 30개 테스트, 커버리지 60%+ 유지.
