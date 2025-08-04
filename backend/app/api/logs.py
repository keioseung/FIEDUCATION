from fastapi import APIRouter, HTTPException, status, Request
from typing import List, Optional
from datetime import datetime, timedelta
import json

from ..firebase_db import get_collection, get_document
from ..firebase_models import FirebaseActivityLog
from ..firebase_auth import get_current_active_user

router = APIRouter()

@router.post("/")
def create_log(
    request: Request,
    log_data: dict
):
    """활동 로그를 생성합니다."""
    try:
        # IP 주소 추출
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        # Firebase에 로그 저장
        log_collection = get_collection('activity_logs')
        if not log_collection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        activity_log = FirebaseActivityLog(
            user_id=log_data.get('user_id'),
            username=log_data.get('username'),
            action=log_data.get('action', ''),
            details=log_data.get('details', ''),
            log_type=log_data.get('log_type', 'user'),
            log_level=log_data.get('log_level', 'info'),
            ip_address=client_ip,
            user_agent=user_agent,
            session_id=log_data.get('session_id')
        )
        
        doc_ref = log_collection.add(activity_log.to_dict())
        
        return {"message": "Log created successfully", "log_id": doc_ref[1].id}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_log: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create log: {str(e)}")

@router.get("/")
def get_logs(
    skip: int = 0,
    limit: int = 100,
    log_type: Optional[str] = None,
    log_level: Optional[str] = None,
    username: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """활동 로그 목록을 조회합니다. (관리자만)"""
    try:
        print(f"🔍 로그 조회 요청 시작")
        print(f"📊 조회 파라미터: skip={skip}, limit={limit}, log_type={log_type}, log_level={log_level}")
        
        log_collection = get_collection('activity_logs')
        if not log_collection:
            return []
        
        # 기본 쿼리
        query = log_collection.order_by('created_at', direction='desc')
        
        # 필터링 (Firebase에서는 클라이언트 사이드에서 필터링)
        docs = query.stream()
        logs = []
        
        for doc in docs:
            log_data = doc.to_dict()
            log_data['id'] = doc.id
            
            # 필터링 적용
            if log_type and log_data.get('log_type') != log_type:
                continue
            if log_level and log_data.get('log_level') != log_level:
                continue
            if username and log_data.get('username') != username:
                continue
            if action and log_data.get('action') != action:
                continue
            
            logs.append(log_data)
        
        # 페이지네이션
        total_logs = len(logs)
        logs = logs[skip:skip + limit]
        
        return {
            "logs": logs,
            "total": total_logs,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        print(f"❌ 로그 조회 에러: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal error during log access: {str(e)}"
            )

@router.get("/simple")
def get_logs_simple(
    skip: int = 0,
    limit: int = 50
):
    """간단한 로그 조회 (인증 없음)"""
    try:
        log_collection = get_collection('activity_logs')
        if not log_collection:
            return []
        
        query = log_collection.order_by('created_at', direction='desc')
        docs = query.stream()
        
        logs = []
        for doc in docs:
            log_data = doc.to_dict()
            log_data['id'] = doc.id
            logs.append(log_data)
        
        # 페이지네이션
        total_logs = len(logs)
        logs = logs[skip:skip + limit]
        
        return {
            "logs": logs,
            "total": total_logs,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        print(f"Error in get_logs_simple: {e}")
        return {"logs": [], "total": 0, "skip": skip, "limit": limit}

@router.get("/stats")
def get_log_stats():
    """로그 통계 조회"""
    try:
        log_collection = get_collection('activity_logs')
        if not log_collection:
            return {"total_logs": 0, "log_types": {}, "log_levels": {}}
        
        docs = log_collection.stream()
        
        total_logs = 0
        log_types = {}
        log_levels = {}
        
        for doc in docs:
            log_data = doc.to_dict()
            total_logs += 1
            
            # 로그 타입 통계
            log_type = log_data.get('log_type', 'unknown')
            log_types[log_type] = log_types.get(log_type, 0) + 1
            
            # 로그 레벨 통계
            log_level = log_data.get('log_level', 'unknown')
            log_levels[log_level] = log_levels.get(log_level, 0) + 1
    
    return {
        "total_logs": total_logs,
            "log_types": log_types,
            "log_levels": log_levels
        }
        
    except Exception as e:
        print(f"Error in get_log_stats: {e}")
        return {"total_logs": 0, "log_types": {}, "log_levels": {}}

@router.delete("/")
def clear_logs():
    """모든 로그 삭제 (관리자만)"""
    try:
        log_collection = get_collection('activity_logs')
        if not log_collection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # 모든 문서 삭제
        docs = log_collection.stream()
        deleted_count = 0
        
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
        
        return {"message": f"All logs deleted successfully", "deleted_count": deleted_count}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in clear_logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")

def log_activity(
    action: str,
    details: str = "",
    log_type: str = "user",
    log_level: str = "info",
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """활동 로그를 기록하는 헬퍼 함수"""
    try:
        log_collection = get_collection('activity_logs')
        if not log_collection:
            print("❌ 로그 컬렉션을 가져올 수 없습니다")
            return
        
        activity_log = FirebaseActivityLog(
            user_id=user_id,
            username=username,
            action=action,
            details=details,
            log_type=log_type,
            log_level=log_level,
            session_id=session_id,
            ip_address=ip_address
        )
        
        log_collection.add(activity_log.to_dict())
        print(f"✅ 활동 로그 기록 완료: {action}")
    
    except Exception as e:
        print(f"❌ 활동 로그 기록 실패: {e}") 