from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

from .firebase_auth import get_user_by_username
from .firebase_models import FirebaseUser

load_dotenv()

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30일

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT 토큰 검증"""
    try:
        print(f"🔐 토큰 검증 시작 - 토큰: {credentials.credentials[:20]}...")
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f"👤 토큰에서 추출된 사용자명: {username}")
        if username is None:
            print("❌ 토큰에 사용자명 없음")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(f"✅ 토큰 검증 성공 - 사용자: {username}")
        return username
    except JWTError as e:
        print(f"❌ JWT 에러: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(username: str = Depends(verify_token)) -> FirebaseUser:
    """현재 로그인한 사용자 정보 조회"""
    print(f"🔍 사용자 조회 시작 - 사용자명: {username}")
    user = get_user_by_username(username)
    if user is None:
        print(f"❌ 사용자 없음 - {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    print(f"✅ 사용자 조회 성공 - {user.username} (역할: {user.role})")
    return user

def get_current_active_user(current_user: FirebaseUser = Depends(get_current_user)) -> FirebaseUser:
    """현재 사용자 정보 조회"""
    return current_user 