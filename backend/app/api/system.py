from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from datetime import datetime

from ..firebase_db import get_collection, test_connection

router = APIRouter()

@router.get("/system-info")
def get_system_info():
    """시스템 정보 조회"""
    try:
        return {
            "system_name": "AI Mastery Hub",
            "version": "1.0.0",
            "database": "Firebase Firestore",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "features": [
                "User Authentication",
                "AI Information Management",
                "Quiz System",
                "Progress Tracking",
                "Activity Logging"
            ]
        }
    except Exception as e:
        print(f"Error in get_system_info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system info")

@router.get("/database-status")
async def get_database_status():
    """데이터베이스 상태 확인"""
    try:
        is_connected = test_connection()
        return {
            "database": "Firebase Firestore",
            "status": "connected" if is_connected else "disconnected",
            "timestamp": datetime.now().isoformat(),
            "connection_test": is_connected
        }
    except Exception as e:
        print(f"Error in get_database_status: {e}")
        return {
            "database": "Firebase Firestore",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "connection_test": False
        }

@router.get("/admin-stats")
async def get_admin_stats():
    """관리자 통계 조회"""
    try:
        stats = {
            "total_users": 0,
            "total_ai_info": 0,
            "total_quizzes": 0,
            "total_logs": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # 사용자 수
        users_collection = get_collection('users')
        if users_collection:
            users_docs = users_collection.stream()
            stats["total_users"] = len(list(users_docs))
        
        # AI 정보 수
        ai_info_collection = get_collection('ai_info')
        if ai_info_collection:
            ai_info_docs = ai_info_collection.stream()
            stats["total_ai_info"] = len(list(ai_info_docs))
        
        # 퀴즈 수
        quiz_collection = get_collection('quiz')
        if quiz_collection:
            quiz_docs = quiz_collection.stream()
            stats["total_quizzes"] = len(list(quiz_docs))
        
        # 로그 수
        logs_collection = get_collection('activity_logs')
        if logs_collection:
            logs_docs = logs_collection.stream()
            stats["total_logs"] = len(list(logs_docs))
        
        return stats
        
    except Exception as e:
        print(f"Error in get_admin_stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get admin stats")

@router.post("/init-database")
async def init_database_tables():
    """데이터베이스 초기화"""
    try:
        # Firebase는 자동으로 컬렉션을 생성하므로 별도 초기화가 필요 없음
        return {
            "message": "Firebase Firestore database is ready",
            "status": "initialized",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error in init_database_tables: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize database") 