# ChurnGuard AI - 고객 이탈 예측 및 분석 시스템

ChurnGuard AI는 고객 이탈 데이터를 분석하고, 고위험군을 식별하며, 실행 가능한 유지 전략을 제공하는 종합 웹 애플리케이션입니다. XGBoost 머신러닝 모델을 활용한 예측 기능과 현대적인 React 프론트엔드를 통한 대화형 시각화를 제공합니다.

## 🚀 주요 기능

-   **대시보드 (Dashboard)**: 주요 지표(총 고객 수, 이탈률) 및 데이터 시각화(계약 형태별 분포, 유지 현황)를 실시간으로 제공합니다.
-   **전략 분석 (Strategy Analysis)**: 통계적 유의성 검정(Chi-square, Mann-Whitney U)을 통해 이탈 원인을 심층 분석하고, 자동화된 대응 전략을 제안합니다.
-   **이탈 예측 (Churn Predictor)**: 개별 고객의 프로필과 사용 패턴을 기반으로 이탈 위험을 예측하고, 맞춤형 제안을 제공하는 대화형 도구입니다 (한국어 지원).
-   **통합 백엔드 시스템**:
    -   **Python (FastAPI)**: AI/ML 예측 및 데이터 분석 담당 (모듈화된 구조).
    -   **Java (Spring Boot)**: H2 데이터베이스를 활용한 고객 데이터 관리.
-   **보안 인증**: JWT (JSON Web Tokens) 기반의 안전한 로그인 시스템.

## 🛠️ 기술 스택 (Tech Stack)

### Backend (AI & Analytics)
-   **Framework**: FastAPI (Python)
-   **ML Model**: XGBoost, Scikit-learn
-   **Data Processing**: Pandas, NumPy, SciPy
-   **Authentication**: OAuth2 with Password (JWT), Passlib (Bcrypt)

### Backend (Data Management)
-   **Framework**: Spring Boot (Java 17)
-   **Database**: H2 Database (In-memory)
-   **ORM**: Spring Data JPA

### Frontend
-   **Framework**: React (Vite)
-   **Styling**: CSS Modules, Framer Motion (Animations)
-   **Icons**: Lucide React
-   **Charts**: Recharts
-   **HTTP Client**: Axios

## 📦 설치 및 실행 (Installation & Setup)

### 사전 요구 사항 (Prerequisites)
-   Python 3.8 이상
-   Node.js 16 이상
-   Java JDK 17 이상

### 1. Python 백엔드 설정 (AI 서버)

1.  백엔드 디렉토리로 이동합니다:
    ```bash
    cd backend
    ```

2.  가상 환경을 생성하고 활성화합니다:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  의존성 패키지를 설치합니다:
    ```bash
    pip install -r requirements.txt
    ```
    *참고: `bcrypt` 관련 오류 발생 시, 3.2.0 버전을 설치하세요.*

4.  서버를 실행합니다:
    ```bash
    python main.py
    ```
    API는 `http://localhost:8000`에서 실행됩니다.

### 2. Java 백엔드 설정 (데이터 서버)

1.  프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다:
    ```bash
    ./gradlew bootRun   # Mac/Linux
    gradlew.bat bootRun # Windows
    ```
    API는 `http://localhost:8080/api/customers`에서 확인 가능하며, H2 콘솔은 `http://localhost:8080/h2-console`에 접속하여 사용할 수 있습니다.

### 3. 프론트엔드 설정

1.  프론트엔드 디렉토리로 이동합니다:
    ```bash
    cd frontend
    ```

2.  패키지를 설치합니다:
    ```bash
    npm install
    ```

3.  개발 서버를 실행합니다:
    ```bash
    npm run dev
    ```
    애플리케이션은 `http://localhost:5173`에서 실행됩니다.

## 📝 사용 방법

1.  브라우저에서 `http://localhost:5173`에 접속합니다.
2.  로그인합니다 (기본 계정 설정이 되어 있다면 해당 계정 사용).
3.  **Dashboard** 탭에서 전체적인 현황을 파악합니다.
4.  **Strategy** 탭에서 AI가 제안하는 인사이트와 유지 전략을 확인합니다.
5.  **Predictor** 탭(한국어)에서 고객 데이터를 입력하고 이탈 위험을 시뮬레이션합니다.
