from fastapi import APIRouter, HTTPException, Response
from typing import List
from datetime import datetime

from ..firebase_db import get_collection, get_document
from ..schemas import BaseContentCreate, BaseContentResponse

router = APIRouter()

@router.get("/", response_model=List[BaseContentResponse])
def get_all_base_content():
    """모든 기본 컨텐츠 조회"""
    try:
        content_collection = get_collection('base_content')
        if not content_collection:
            return []
        
        docs = content_collection.order_by('created_at', direction='desc').stream()
        contents = []
        for doc in docs:
            content_data = doc.to_dict()
            content_data['id'] = doc.id
            contents.append(content_data)
        
        return contents
    except Exception as e:
        print(f"Error in get_all_base_content: {e}")
        return []

@router.post("/", response_model=BaseContentResponse)
def add_base_content(content_data: BaseContentCreate):
    """새 기본 컨텐츠 추가"""
    try:
        content_collection = get_collection('base_content')
        if not content_collection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        content_dict = {
            'title': content_data.title,
            'content': content_data.content,
            'category': content_data.category,
            'created_at': datetime.now().isoformat()
        }
        
        doc_ref = content_collection.add(content_dict)
        content_dict['id'] = doc_ref[1].id
        
        return content_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_base_content: {e}")
        raise HTTPException(status_code=500, detail="Failed to add base content")

@router.options("/")
def options_base_content():
    """OPTIONS 요청 처리"""
    return {"message": "OK"} 