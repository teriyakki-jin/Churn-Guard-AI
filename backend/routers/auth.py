import re
import time as _time
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from datetime import timedelta
from auth import Token, authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from db_models import User
from starlette.requests import Request
from limiter import limiter
from logger import logger

router = APIRouter()

# Account lockout tracking
_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 300  # 5 minutes
_login_failures: dict = defaultdict(lambda: {"count": 0, "locked_until": 0.0})


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', v):
            raise ValueError("Username must be 3-30 characters (letters, digits, underscore)")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain a digit")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>\-_=+\[\]~`]', v):
            raise ValueError("Password must contain a special character")
        return v

@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    lock_key = f"{form_data.username}:{client_ip}"
    tracker = _login_failures[lock_key]

    # Check lockout
    if tracker["locked_until"] > _time.time():
        remaining = int(tracker["locked_until"] - _time.time())
        logger.warning(f"Locked account login attempt: user={form_data.username} ip={client_ip} remaining={remaining}s")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked. Try again in {remaining} seconds.",
        )

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        tracker["count"] += 1
        logger.warning(f"Failed login attempt ({tracker['count']}/{_MAX_ATTEMPTS}): user={form_data.username} ip={client_ip}")
        if tracker["count"] >= _MAX_ATTEMPTS:
            tracker["locked_until"] = _time.time() + _LOCKOUT_SECONDS
            tracker["count"] = 0
            logger.warning(f"Account locked for {_LOCKOUT_SECONDS}s: user={form_data.username} ip={client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed attempts. Account locked for {_LOCKOUT_SECONDS // 60} minutes.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reset on success
    _login_failures.pop(lock_key, None)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"Successful login: user={user.username} ip={client_ip}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if db.query(User).filter(User.username == body.username).first():
        logger.warning(f"Duplicate registration attempt: user={body.username} ip={client_ip}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.username,
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    logger.info(f"New user registered: user={body.username} ip={client_ip}")
    return {"message": "Registration successful"}
