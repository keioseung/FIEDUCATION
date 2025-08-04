from fastapi import APIRouter, HTTPException, Response
from typing import List
import json
import feedparser
import re
import html
from deep_translator import GoogleTranslator

from ..firebase_db import get_collection, get_document
from ..firebase_models import FirebaseAIInfo
from ..schemas import AIInfoCreate, AIInfoResponse, AIInfoItem, TermItem

router = APIRouter()

def translate_to_ko(text):
    try:
        return GoogleTranslator(source='auto', target='ko').translate(text)
    except Exception:
        return text

def clean_summary(summary, title):
    text = re.sub(r'<[^>]+>', '', summary)
    text = html.unescape(text)
    text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
    if len(text) < 10 or text.replace(' ', '') in title.replace(' ', ''):
        return None
    return text

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[-–—:·.,!?"\'\\|/]', '', text)
    text = re.sub(r'\s+', '', text)
    return text

@router.get("/{date}", response_model=List[AIInfoItem])
def get_ai_info_by_date(date: str):
    """특정 날짜의 AI 정보 조회"""
    try:
        # Firebase에서 해당 날짜의 AI 정보 조회
        ai_info_ref = get_document('ai_info', date)
        if not ai_info_ref:
            return []
        
        doc = ai_info_ref.get()
        if not doc.exists:
            return []
        
        ai_info_data = doc.to_dict()
        ai_info = FirebaseAIInfo.from_dict(ai_info_data)
        
        infos = []
        if ai_info.info1_title and ai_info.info1_content:
            try:
                terms1 = json.loads(ai_info.info1_terms) if ai_info.info1_terms else []
            except json.JSONDecodeError:
                terms1 = []
            infos.append({
                "title": ai_info.info1_title, 
                "content": ai_info.info1_content,
                "terms": terms1
            })
        if ai_info.info2_title and ai_info.info2_content:
            try:
                terms2 = json.loads(ai_info.info2_terms) if ai_info.info2_terms else []
            except json.JSONDecodeError:
                terms2 = []
            infos.append({
                "title": ai_info.info2_title, 
                "content": ai_info.info2_content,
                "terms": terms2
            })
        if ai_info.info3_title and ai_info.info3_content:
            try:
                terms3 = json.loads(ai_info.info3_terms) if ai_info.info3_terms else []
            except json.JSONDecodeError:
                terms3 = []
            infos.append({
                "title": ai_info.info3_title, 
                "content": ai_info.info3_content,
                "terms": terms3
            })
        
        return infos
    except Exception as e:
        print(f"Error in get_ai_info_by_date: {e}")
        return []

@router.post("/", response_model=AIInfoResponse)
def add_ai_info(ai_info_data: AIInfoCreate):
    """AI 정보 추가"""
    try:
        # Firebase에 AI 정보 저장
        ai_info_collection = get_collection('ai_info')
        if not ai_info_collection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # 기존 데이터 확인
        existing_doc = ai_info_collection.document(ai_info_data.date).get()
        if existing_doc.exists:
            raise HTTPException(status_code=400, detail="AI info for this date already exists")
        
        # 새 AI 정보 생성
        firebase_ai_info = FirebaseAIInfo(
            date=ai_info_data.date,
            info1_title=ai_info_data.info1_title,
            info1_content=ai_info_data.info1_content,
            info1_terms=json.dumps(ai_info_data.info1_terms) if ai_info_data.info1_terms else None,
            info2_title=ai_info_data.info2_title,
            info2_content=ai_info_data.info2_content,
            info2_terms=json.dumps(ai_info_data.info2_terms) if ai_info_data.info2_terms else None,
            info3_title=ai_info_data.info3_title,
            info3_content=ai_info_data.info3_content,
            info3_terms=json.dumps(ai_info_data.info3_terms) if ai_info_data.info3_terms else None
        )
        
        # Firebase에 저장
        ai_info_collection.document(ai_info_data.date).set(firebase_ai_info.to_dict())
        
        return {
            "message": "AI info added successfully",
            "date": ai_info_data.date
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_ai_info: {e}")
        raise HTTPException(status_code=500, detail="Failed to add AI info")

@router.delete("/{date}")
def delete_ai_info(date: str):
    """특정 날짜의 AI 정보 삭제"""
    try:
        ai_info_ref = get_document('ai_info', date)
        if not ai_info_ref:
            raise HTTPException(status_code=404, detail="AI info not found")
        
        ai_info_ref.delete()
        return {"message": "AI info deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_ai_info: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete AI info")

@router.get("/dates/all")
def get_all_ai_info_dates():
    """모든 AI 정보 날짜 조회"""
    try:
        ai_info_collection = get_collection('ai_info')
        if not ai_info_collection:
            return []
        
        docs = ai_info_collection.stream()
        dates = [doc.id for doc in docs]
        return sorted(dates, reverse=True)
    except Exception as e:
        print(f"Error in get_all_ai_info_dates: {e}")
        return []

@router.get("/news/fetch")
def fetch_ai_news():
    """AI 관련 뉴스 가져오기"""
    try:
        # RSS 피드에서 AI 뉴스 가져오기
        feed = feedparser.parse('https://feeds.feedburner.com/TechCrunch/')
        
        news_items = []
        for entry in feed.entries[:10]:
            title = entry.title
            summary = clean_summary(entry.summary, title)
            
            if summary:
                # 한국어로 번역
                translated_title = translate_to_ko(title)
                translated_summary = translate_to_ko(summary)
                
                news_items.append({
                    "title": translated_title,
                    "summary": translated_summary,
                    "link": entry.link,
                    "published": entry.published
                })
        
        return {"news": news_items}
    except Exception as e:
        print(f"Error in fetch_ai_news: {e}")
        return {"news": []}

@router.options("/")
def options_ai_info():
    """OPTIONS 요청 처리"""
    return {"message": "OK"} 