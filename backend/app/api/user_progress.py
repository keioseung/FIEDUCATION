from fastapi import APIRouter, HTTPException, Response
from typing import List, Optional
from datetime import datetime
import json

from ..firebase_db import get_collection, get_document
from ..firebase_models import FirebaseUserProgress
from ..schemas import UserProgressCreate, UserProgressResponse

router = APIRouter()

@router.get("/{session_id}")
def get_user_progress(session_id: str):
    """사용자 진행상황 조회"""
    try:
        progress_collection = get_collection('user_progress')
        if not progress_collection:
            return []
        
        query = progress_collection.where('session_id', '==', session_id)
        docs = query.stream()
        
        progress_list = []
        for doc in docs:
            progress_data = doc.to_dict()
            progress_data['id'] = doc.id
            progress_list.append(progress_data)
        
        return progress_list
    except Exception as e:
        print(f"Error in get_user_progress: {e}")
        return []

@router.post("/", response_model=UserProgressResponse)
def add_user_progress(progress_data: UserProgressCreate):
    """사용자 진행상황 추가"""
    try:
        progress_collection = get_collection('user_progress')
        if not progress_collection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        progress_dict = {
            'session_id': progress_data.session_id,
            'date': progress_data.date,
            'learned_info': json.dumps(progress_data.learned_info) if progress_data.learned_info else None,
            'quiz_score': progress_data.quiz_score,
            'created_at': datetime.now().isoformat()
        }
        
        doc_ref = progress_collection.add(progress_dict)
        progress_dict['id'] = doc_ref[1].id
        
        return progress_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_user_progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to add user progress")

@router.get("/stats/{session_id}")
def get_user_stats(session_id: str):
    """사용자 통계 조회"""
    try:
        progress_collection = get_collection('user_progress')
        if not progress_collection:
            return {"total_days": 0, "total_quiz_score": 0, "average_score": 0}
        
        query = progress_collection.where('session_id', '==', session_id)
        docs = query.stream()
        
        total_days = 0
        total_quiz_score = 0
        scores = []
        
        for doc in docs:
            progress_data = doc.to_dict()
            if progress_data.get('date') != '__stats__':
                total_days += 1
                if progress_data.get('quiz_score') is not None:
                    total_quiz_score += progress_data['quiz_score']
                    scores.append(progress_data['quiz_score'])
        
        average_score = total_quiz_score / len(scores) if scores else 0
    
    return {
            "total_days": total_days,
            "total_quiz_score": total_quiz_score,
            "average_score": round(average_score, 2)
        }
    except Exception as e:
        print(f"Error in get_user_stats: {e}")
        return {"total_days": 0, "total_quiz_score": 0, "average_score": 0}

@router.options("/")
def options_user_progress():
    """OPTIONS 요청 처리"""
    return {"message": "OK"} 