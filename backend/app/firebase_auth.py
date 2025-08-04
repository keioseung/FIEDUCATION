from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from .firebase_db import get_collection, get_document
from .firebase_models import FirebaseUser

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your-secret-key-here"  # 실제 배포 시 환경변수로 설정
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """JWT 토큰 검증 및 사용자명 반환"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def get_user_by_username(username: str) -> Optional[FirebaseUser]:
    """사용자명으로 사용자 조회"""
    try:
        print(f"🔍 사용자 조회 시작: {username}")
        
        users_ref = get_collection('users')
        if not users_ref:
            print("❌ users 컬렉션 참조를 가져올 수 없습니다")
            return None
        
        print(f"✅ users 컬렉션 참조 성공")
        
        # 사용자명으로 쿼리
        query = users_ref.where('username', '==', username).limit(1)
        print(f"🔍 쿼리 실행: username == {username}")
        
        docs = query.stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            print(f"✅ 사용자 발견: {username} (ID: {doc.id})")
            return FirebaseUser.from_dict(user_data, doc.id)
        
        print(f"ℹ️ 사용자를 찾을 수 없음: {username}")
        return None
    except Exception as e:
        print(f"❌ 사용자 조회 실패: {e}")
        print(f"🔍 에러 타입: {type(e)}")
        import traceback
        print(f"📋 상세 에러: {traceback.format_exc()}")
        return None

def get_user_by_id(user_id: str) -> Optional[FirebaseUser]:
    """사용자 ID로 사용자 조회"""
    try:
        user_doc = get_document('users', user_id)
        if not user_doc:
            return None
        
        doc = user_doc.get()
        if doc.exists:
            user_data = doc.to_dict()
            return FirebaseUser.from_dict(user_data, doc.id)
        
        return None
    except Exception as e:
        print(f"❌ 사용자 ID 조회 실패: {e}")
        return None

def create_user(user: FirebaseUser) -> Optional[str]:
    """새 사용자 생성"""
    try:
        print(f"🔍 사용자 생성 시작: {user.username}")
        
        users_ref = get_collection('users')
        if not users_ref:
            print("❌ users 컬렉션 참조를 가져올 수 없습니다")
            return None
        
        print(f"✅ users 컬렉션 참조 성공")
        
        # 사용자명 중복 확인
        existing_user = get_user_by_username(user.username)
        if existing_user:
            print(f"❌ 사용자명 중복: {user.username}")
            return None
        
        print(f"✅ 사용자명 중복 확인 완료: {user.username}")
        
        # 새 사용자 문서 생성
        user_data = user.to_dict()
        user_data['created_at'] = datetime.utcnow()
        
        print(f"📝 사용자 데이터 준비 완료: {user_data}")
        
        doc_ref = users_ref.add(user_data)
        
        print(f"✅ 사용자 생성 성공: {user.username}")
        print(f"📄 생성된 문서 ID: {doc_ref[1].id}")
        return doc_ref[1].id  # 생성된 문서 ID 반환
        
    except Exception as e:
        print(f"❌ 사용자 생성 실패: {e}")
        print(f"🔍 에러 타입: {type(e)}")
        import traceback
        print(f"📋 상세 에러: {traceback.format_exc()}")
        return None

def update_user(user_id: str, user_data: dict) -> bool:
    """사용자 정보 업데이트"""
    try:
        user_doc = get_document('users', user_id)
        if not user_doc:
            return False
        
        user_doc.update(user_data)
        print(f"✅ 사용자 업데이트 성공: {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ 사용자 업데이트 실패: {e}")
        return False

def delete_user(user_id: str) -> bool:
    """사용자 삭제"""
    try:
        user_doc = get_document('users', user_id)
        if not user_doc:
            return False
        
        user_doc.delete()
        print(f"✅ 사용자 삭제 성공: {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ 사용자 삭제 실패: {e}")
        return False

def get_all_users() -> list[FirebaseUser]:
    """모든 사용자 조회"""
    try:
        users_ref = get_collection('users')
        if not users_ref:
            return []
        
        users = []
        docs = users_ref.stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            user = FirebaseUser.from_dict(user_data, doc.id)
            users.append(user)
        
        return users
        
    except Exception as e:
        print(f"❌ 모든 사용자 조회 실패: {e}")
        return []

def authenticate_user(username: str, password: str) -> Optional[FirebaseUser]:
    """사용자 인증"""
    try:
        user = get_user_by_username(username)
        if not user:
            print(f"❌ 사용자를 찾을 수 없음: {username}")
            return None
        
        if not verify_password(password, user.hashed_password):
            print(f"❌ 비밀번호가 일치하지 않음: {username}")
            return None
        
        print(f"✅ 사용자 인증 성공: {username}")
        return user
        
    except Exception as e:
        print(f"❌ 사용자 인증 실패: {e}")
        return None

def get_current_active_user(token: str) -> Optional[FirebaseUser]:
    """현재 활성 사용자 조회"""
    try:
        username = verify_token(token)
        if username is None:
            return None
        
        user = get_user_by_username(username)
        if user is None:
            return None
        
        return user
        
    except Exception as e:
        print(f"❌ 현재 사용자 조회 실패: {e}")
        return None 