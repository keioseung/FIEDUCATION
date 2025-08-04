from fastapi import APIRouter, HTTPException, Response
from typing import List
from datetime import datetime

from ..firebase_db import get_collection, get_document
from ..schemas import TermCreate, TermResponse

router = APIRouter()

@router.get("/", response_model=List[TermResponse])
def get_all_terms():
    """모든 용어 조회"""
    try:
        term_collection = get_collection('term')
        if not term_collection:
            return []
        
        docs = term_collection.order_by('created_at', direction='desc').stream()
        terms = []
        for doc in docs:
            term_data = doc.to_dict()
            term_data['id'] = doc.id
            terms.append(term_data)
        
        return terms
    except Exception as e:
        print(f"Error in get_all_terms: {e}")
        return []

@router.post("/", response_model=TermResponse)
def add_term(term_data: TermCreate):
    """새 용어 추가"""
    try:
        term_collection = get_collection('term')
        if not term_collection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        term_dict = {
            'term': term_data.term,
            'description': term_data.description,
            'category': term_data.category,
            'created_at': datetime.now().isoformat()
        }
        
        doc_ref = term_collection.add(term_dict)
        term_dict['id'] = doc_ref[1].id
        
        return term_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_term: {e}")
        raise HTTPException(status_code=500, detail="Failed to add term")

@router.options("/")
def options_term():
    """OPTIONS 요청 처리"""
    return {"message": "OK"} 