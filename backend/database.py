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

def init_db():
    """데이터베이스 초기화"""
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully!")
    
    # 기본 관리자 계정 생성
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin_user = User(
                username="admin",
                email="admin@churnguard.ai",
                hashed_password=pwd_context.hash("password123"),
                full_name="Admin User",
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Admin user created: admin / password123")
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
