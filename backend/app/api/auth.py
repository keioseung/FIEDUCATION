from fastapi import APIRouter, Depends, HTTPException, status, Request
from datetime import timedelta

from ..firebase_auth import (
    verify_password, get_password_hash, create_access_token, 
    authenticate_user, get_current_active_user, create_user, 
    get_all_users, update_user, delete_user, get_user_by_username, ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..firebase_models import FirebaseUser
from ..schemas import UserCreate, UserLogin, UserResponse, Token
from .logs import log_activity

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, request: Request):
    """사용자 회원가입"""
    try:
        print(f"📝 회원가입 시도: {user_data.username}")
        
        # 새 사용자 생성
        hashed_password = get_password_hash(user_data.password)
        firebase_user = FirebaseUser(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role or "user"
        )
        
        # Firebase에 사용자 생성
        user_id = create_user(firebase_user)
        if not user_id:
            print("❌ 사용자 생성 실패")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered or creation failed"
            )
        
        # 생성된 사용자 정보 반환
        firebase_user.user_id = user_id
        
        print(f"✅ 회원가입 성공: {user_data.username}")
        
        # 회원가입 로그 기록 (에러 무시)
        try:
            log_activity(
                action="회원가입",
                details=f"새 사용자가 등록되었습니다. 역할: {user_data.role}",
                log_type="user",
                log_level="info",
                user_id=user_id,
                username=firebase_user.username,
                ip_address=request.client.host if request.client else None
            )
        except Exception as log_error:
            print(f"⚠️ 로그 기록 실패 (무시): {log_error}")
        
        # UserResponse 스키마에 맞는 형태로 반환
        return {
            "id": int(user_id) if user_id.isdigit() else 1,  # Firebase ID를 정수로 변환
            "username": firebase_user.username,
            "email": firebase_user.email,
            "role": firebase_user.role,
            "created_at": firebase_user.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 회원가입 중 예외 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/init-db")
def initialize_database():
    """Firebase 데이터베이스 초기화 및 테스트 사용자 생성"""
    try:
        print("🗄️ Firebase 데이터베이스 초기화 시작...")
        
        # Firebase 초기화
        from ..firebase_db import initialize_firebase
        if not initialize_firebase():
            raise Exception("Firebase 초기화 실패")
        
        # 기본 사용자 확인/생성
        admin_user = get_user_by_username("admin")
        admin_created = False
        if not admin_user:
            admin_user = FirebaseUser(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            user_id = create_user(admin_user)
            if user_id:
                admin_user.user_id = user_id
                admin_created = True
                print("✅ 관리자 계정 생성: admin/admin123")
            else:
                print("❌ 관리자 계정 생성 실패")
        
        test_user = get_user_by_username("user")
        test_user_created = False
        if not test_user:
            test_user = FirebaseUser(
                username="user",
                email="user@example.com",
                hashed_password=get_password_hash("user123"),
                role="user"
            )
            user_id = create_user(test_user)
            if user_id:
                test_user.user_id = user_id
                test_user_created = True
                print("✅ 테스트 사용자 계정 생성: user/user123")
            else:
                print("❌ 테스트 사용자 계정 생성 실패")
        
        print("✅ Firebase 데이터베이스 초기화 완료")
        
        return {
            "message": "Firebase database initialized successfully",
            "admin_created": admin_created,
            "test_user_created": test_user_created
        }
        
    except Exception as e:
        print(f"💥 Firebase 데이터베이스 초기화 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Firebase database initialization failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, request: Request):
    """사용자 로그인"""
    try:
        print(f"🔍 로그인 시도: {user_credentials.username}")
        
        # Firebase에서 사용자 인증
        user = authenticate_user(user_credentials.username, user_credentials.password)
        print(f"👤 사용자 인증 결과: {user is not None}")
        
        if not user:
            print("❌ 인증 실패")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        print(f"🎫 토큰 생성 완료: {access_token[:20]}...")
        
        # 로그인 로그 기록 (에러 무시)
        try:
            log_activity(
                action="로그인",
                details=f"사용자가 성공적으로 로그인했습니다. 역할: {user.role}",
                log_type="user",
                log_level="success",
                user_id=user.user_id,
                username=user.username,
                ip_address=request.client.host if request.client else None
            )
        except Exception as log_error:
            print(f"⚠️ 로그 기록 실패 (무시): {log_error}")
        
        print("✅ 로그인 성공")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 로그인 중 예외 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: FirebaseUser = Depends(get_current_active_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user

@router.get("/users", response_model=list[UserResponse])
def get_all_users(current_user: FirebaseUser = Depends(get_current_active_user)):
    """모든 사용자 조회 (관리자만)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = get_all_users()
    return users

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: str, 
    role_data: dict,
    current_user: FirebaseUser = Depends(get_current_active_user)
):
    """사용자 역할 변경 (관리자만)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    new_role = role_data.get('role')
    if new_role not in ['user', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    success = update_user(user_id, {'role': new_role})
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User role updated successfully"}

@router.delete("/users/{user_id}")
def delete_user_endpoint(
    user_id: str,
    current_user: FirebaseUser = Depends(get_current_active_user)
):
    """사용자 삭제 (관리자만)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 자기 자신은 삭제할 수 없음
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"} 