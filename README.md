# ChurnGuard AI

통신사 고객 데이터를 기반으로 이탈 위험을 예측하고, 데이터 기반 유지 전략을 제안하는 웹 애플리케이션입니다.

## 1. 문제 정의
고객 이탈은 기업의 매출과 LTV에 직접적인 영향을 줍니다. 본 프로젝트는 이탈 고위험 고객을 조기에 식별하고, 우선 대응 전략을 제시하는 것을 목표로 합니다.

## 2. 접근 방법
- Voting Ensemble(XGBoost + RandomForest + GradientBoosting)로 예측 안정성 확보
- 예측 결과와 함께 위험 요인(Risk Factors) 및 대응 전략을 함께 제공
- 실시간 시뮬레이션(WebSocket)과 A/B 테스트 라우팅으로 운영 검증 지원

## 3. 주요 기능
- 실시간 KPI 대시보드 및 이탈 원인 분석
- 개별 고객 이탈 확률(0~100%) 예측
- 맞춤형 유지 전략 자동 제안
- 실시간 시뮬레이션 및 모델 비교(A/B)
- CSV/PDF 리포트 내보내기 및 이메일 발송
- JWT 인증, 계정 잠금, 비밀번호 정책 등 보안 기능

## 4. 기술 스택
- Frontend: React, Vite, Recharts, Framer Motion
- Backend: FastAPI, SQLAlchemy, Pydantic
- ML: XGBoost, RandomForest, GradientBoosting
- Auth: JWT, OAuth2 Bearer, bcrypt
- Infra: Docker, Docker Compose, Nginx, GitHub Actions

## 5. 프로젝트 구조
```text
Churn-Guard-AI/
├── backend/
├── frontend/
├── nginx/
├── .github/workflows/
├── docker-compose.yml
└── README.md
```

## 6. 실행 방법
```bash
# Docker 실행(권장)
git clone https://github.com/teriyakki-jin/Churn-Guard-AI.git
cd Churn-Guard-AI
cp env.example .env
docker-compose up --build
```

## 7. 서비스 엔드포인트
- Frontend: http://localhost:5173
- Backend API: http://localhost:8002
- API Docs: http://localhost:8002/docs

## 8. 결과 및 확장 방향
- 이탈 위험 고객 선별 및 대응 자동화로 운영 의사결정 속도 향상
- 모델 모니터링 및 피처 스토어 도입으로 재현성/운영성 강화 예정
