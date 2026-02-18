from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Base, User
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 URL 설정
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./churn_guard.db")

# SQLite의 경우 check_same_thread=False 추가
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _is_true(value: str) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def init_db():
    """데이터베이스 초기화"""
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully!")

    # Optional admin bootstrap (disabled by default for security)
    if not _is_true(os.getenv("BOOTSTRAP_ADMIN", "false")):
        return

    admin_username = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
    if not admin_password:
        print("[WARN] BOOTSTRAP_ADMIN_PASSWORD is not set; skipping admin bootstrap")
        return

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == admin_username).first():
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin_user = User(
                username=admin_username,
                email=os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@churnguard.ai"),
                hashed_password=pwd_context.hash(admin_password),
                full_name="Admin User",
                is_active=True,
                is_admin=True,
            )
            db.add(admin_user)
            db.commit()
            print(f"[OK] Admin user bootstrapped: {admin_username}")
    except Exception as e:
        print(f"[ERROR] Error creating admin user: {e}")
    finally:
        db.close()


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 애플리케이션 시작 시 데이터베이스 초기화
if __name__ == "__main__":
    init_db()
