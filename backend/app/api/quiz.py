from fastapi import APIRouter, HTTPException, Response
from typing import List
import json

from ..firebase_db import get_collection, get_document
from ..schemas import QuizCreate, QuizResponse

router = APIRouter()

@router.get("/topics", response_model=List[str])
def get_all_quiz_topics():
    """모든 퀴즈 주제 조회"""
    try:
        quiz_collection = get_collection('quiz')
        if not quiz_collection:
            return []
        
        docs = quiz_collection.stream()
        topics = list(set([doc.to_dict().get('topic', '') for doc in docs if doc.to_dict().get('topic')]))
        return topics
    except Exception as e:
        print(f"Error in get_all_quiz_topics: {e}")
        return []

@router.get("/{topic}", response_model=List[QuizResponse])
def get_quiz_by_topic(topic: str):
    """특정 주제의 퀴즈 조회"""
    try:
        quiz_collection = get_collection('quiz')
        if not quiz_collection:
            return []
        
        query = quiz_collection.where('topic', '==', topic)
        docs = query.stream()
        
        quizzes = []
        for doc in docs:
            quiz_data = doc.to_dict()
            quiz_data['id'] = doc.id
            quizzes.append(quiz_data)
        
        return quizzes
    except Exception as e:
        print(f"Error in get_quiz_by_topic: {e}")
        return []

@router.post("/", response_model=QuizResponse)
def add_quiz(quiz_data: QuizCreate):
    """새 퀴즈 추가"""
    try:
        quiz_collection = get_collection('quiz')
        if not quiz_collection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        quiz_dict = {
            'topic': quiz_data.topic,
            'question': quiz_data.question,
            'option1': quiz_data.option1,
            'option2': quiz_data.option2,
            'option3': quiz_data.option3,
            'option4': quiz_data.option4,
            'correct': quiz_data.correct,
            'explanation': quiz_data.explanation
        }
        
        doc_ref = quiz_collection.add(quiz_dict)
        quiz_dict['id'] = doc_ref[1].id
        
        return quiz_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to add quiz")

@router.put("/{quiz_id}", response_model=QuizResponse)
def update_quiz(quiz_id: str, quiz_data: QuizCreate):
    """퀴즈 수정"""
    try:
        quiz_ref = get_document('quiz', quiz_id)
        if not quiz_ref:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        doc = quiz_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        quiz_dict = {
            'topic': quiz_data.topic,
            'question': quiz_data.question,
            'option1': quiz_data.option1,
            'option2': quiz_data.option2,
            'option3': quiz_data.option3,
            'option4': quiz_data.option4,
            'correct': quiz_data.correct,
            'explanation': quiz_data.explanation
        }
        
        quiz_ref.update(quiz_dict)
        quiz_dict['id'] = quiz_id
        
        return quiz_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to update quiz")

@router.delete("/{quiz_id}")
def delete_quiz(quiz_id: str):
    """퀴즈 삭제"""
    try:
        quiz_ref = get_document('quiz', quiz_id)
        if not quiz_ref:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        quiz_ref.delete()
        return {"message": "Quiz deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete quiz")

@router.get("/generate/{topic}")
def generate_quiz(topic: str):
    """주제에 따른 퀴즈를 생성합니다."""
    # 간단한 퀴즈 생성 로직 (실제로는 더 복잡한 로직이 필요)
    quiz_templates = {
        "AI": {
            "question": "인공지능(AI)의 정의로 가장 적절한 것은?",
            "options": [
                "컴퓨터가 인간처럼 생각하는 기술",
                "인간의 지능을 모방하는 컴퓨터 시스템",
                "자동화된 기계 시스템",
                "데이터 처리 프로그램"
            ],
            "correct": 1,
            "explanation": "AI는 인간의 지능을 모방하여 학습하고 추론하는 컴퓨터 시스템입니다."
        },
        "머신러닝": {
            "question": "머신러닝의 주요 특징은?",
            "options": [
                "사전에 정의된 규칙만 사용",
                "데이터로부터 패턴을 학습",
                "인간의 개입이 필요 없음",
                "결과가 항상 정확함"
            ],
            "correct": 1,
            "explanation": "머신러닝은 데이터로부터 패턴을 학습하여 예측이나 분류를 수행합니다."
        }
    }
    
    if topic in quiz_templates:
        template = quiz_templates[topic]
        return {
            "question": template["question"],
            "option1": template["options"][0],
            "option2": template["options"][1],
            "option3": template["options"][2],
            "option4": template["options"][3],
            "correct": template["correct"],
            "explanation": template["explanation"]
        }
    else:
        return {
            "question": f"{topic}에 대한 기본 퀴즈",
            "option1": "옵션 1",
            "option2": "옵션 2",
            "option3": "옵션 3",
            "option4": "옵션 4",
            "correct": 0,
            "explanation": "기본 퀴즈입니다."
        }

@router.options("/")
def options_quiz():
    """OPTIONS 요청 처리"""
    return {"message": "OK"} 