from fastapi import APIRouter, HTTPException, Response
from typing import List
from datetime import datetime

from ..firebase_db import get_collection, get_document
from ..schemas import PromptCreate, PromptResponse

router = APIRouter()

@router.get("/", response_model=List[PromptResponse])
def get_all_prompts():
    """모든 프롬프트 조회"""
    try:
        prompt_collection = get_collection('prompt')
        if not prompt_collection:
            return []
        
        docs = prompt_collection.order_by('created_at', direction='desc').stream()
        prompts = []
        for doc in docs:
            prompt_data = doc.to_dict()
            prompt_data['id'] = doc.id
            prompts.append(prompt_data)
        
        return prompts
    except Exception as e:
        print(f"Error in get_all_prompts: {e}")
        return []

@router.post("/", response_model=PromptResponse)
def add_prompt(prompt_data: PromptCreate):
    """새 프롬프트 추가"""
    try:
        prompt_collection = get_collection('prompt')
        if not prompt_collection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        prompt_dict = {
            'title': prompt_data.title,
            'content': prompt_data.content,
            'category': prompt_data.category,
            'created_at': datetime.now().isoformat()
        }
        
        doc_ref = prompt_collection.add(prompt_dict)
        prompt_dict['id'] = doc_ref[1].id
        
        return prompt_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to add prompt")

@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: str, prompt_data: PromptCreate):
    """프롬프트 수정"""
    try:
        prompt_ref = get_document('prompt', prompt_id)
        if not prompt_ref:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        doc = prompt_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        prompt_dict = {
            'title': prompt_data.title,
            'content': prompt_data.content,
            'category': prompt_data.category
        }
        
        prompt_ref.update(prompt_dict)
        prompt_dict['id'] = prompt_id
        
        return prompt_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to update prompt")

@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: str):
    """프롬프트 삭제"""
    try:
        prompt_ref = get_document('prompt', prompt_id)
        if not prompt_ref:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        prompt_ref.delete()
        return {"message": "Prompt deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete prompt")

@router.get("/category/{category}", response_model=List[PromptResponse])
def get_prompts_by_category(category: str):
    """카테고리별 프롬프트 조회"""
    try:
        prompt_collection = get_collection('prompt')
        if not prompt_collection:
            return []
        
        query = prompt_collection.where('category', '==', category)
        docs = query.stream()
        
        prompts = []
        for doc in docs:
            prompt_data = doc.to_dict()
            prompt_data['id'] = doc.id
            prompts.append(prompt_data)
        
        return prompts
    except Exception as e:
        print(f"Error in get_prompts_by_category: {e}")
        return []

@router.options("/")
def options_prompt():
    """OPTIONS 요청 처리"""
    return {"message": "OK"} 