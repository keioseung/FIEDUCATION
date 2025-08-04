from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserLogin, UserResponse, Token
from ..auth import verify_password, get_password_hash, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
from .logs import log_activity

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    try:
        print(f"📝 회원가입 시도: {user_data.username}")
        
        # 중복 사용자명 확인
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            print("❌ 사용자명 중복")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # 중복 이메일 확인 (이메일이 제공된 경우)
        if user_data.email:
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                print("❌ 이메일 중복")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # 새 사용자 생성
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role or "user"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"✅ 회원가입 성공: {user_data.username}")
        
        # 회원가입 로그 기록 (에러 무시)
        try:
            log_activity(
                db=db,
                action="회원가입",
                details=f"새 사용자가 등록되었습니다. 역할: {user_data.role}",
                log_type="user",
                log_level="info",
                user_id=db_user.id,
                username=db_user.username,
                ip_address=request.client.host if request.client else None
            )
        except Exception as log_error:
            print(f"⚠️ 로그 기록 실패 (무시): {log_error}")
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 회원가입 중 예외 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/init-db")
def initialize_database(db: Session = Depends(get_db)):
    """데이터베이스 초기화 및 테스트 사용자 생성"""
    try:
        print("🗄️ 데이터베이스 초기화 시작...")
        
        # 모든 테이블 생성
        from ..models import Base
        from ..database import engine
        Base.metadata.create_all(bind=engine)
        print("✅ 테이블 생성 완료")
        
        # 기본 사용자 확인/생성
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin_user)
            print("✅ 관리자 계정 생성: admin/admin123")
        
        test_user = db.query(User).filter(User.username == "user").first()
        if not test_user:
            test_user = User(
                username="user",
                email="user@example.com",
                hashed_password=get_password_hash("user123"),
                role="user"
            )
            db.add(test_user)
            print("✅ 테스트 사용자 계정 생성: user/user123")
        
        db.commit()
        print("✅ 데이터베이스 초기화 완료")
        
        return {
            "message": "Database initialized successfully",
            "admin_created": admin_user is None,
            "test_user_created": test_user is None
        }
        
    except Exception as e:
        print(f"💥 데이터베이스 초기화 실패: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database initialization failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """사용자 로그인"""
    try:
        print(f"🔍 로그인 시도: {user_credentials.username}")
        
        # 사용자 확인
        user = db.query(User).filter(User.username == user_credentials.username).first()
        print(f"👤 사용자 조회 결과: {user is not None}")
        
        if not user:
            print("❌ 사용자를 찾을 수 없음")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 비밀번호 확인
        password_valid = verify_password(user_credentials.password, user.hashed_password)
        print(f"🔐 비밀번호 확인 결과: {password_valid}")
        
        if not password_valid:
            print("❌ 비밀번호가 일치하지 않음")
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
                db=db,
                action="로그인",
                details=f"사용자가 성공적으로 로그인했습니다. 역할: {user.role}",
                log_type="user",
                log_level="success",
                user_id=user.id,
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
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user

@router.get("/users", response_model=list[UserResponse])
def get_all_users(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """모든 사용자 조회 (관리자만)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).all()
    return users

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int, 
    role_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 역할 변경 (관리자만)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    new_role = role_data.get('role')
    if new_role not in ['user', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    user.role = new_role
    db.commit()
    
    return {"message": "User role updated successfully"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 삭제 (관리자만)"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 자기 자신은 삭제할 수 없음
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"} 