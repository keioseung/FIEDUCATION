from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from .firebase_db import get_collection, get_document

# Firebase 기반 사용자 모델
class FirebaseUser:
    def __init__(self, username: str, email: Optional[str] = None, 
                 hashed_password: str = "", role: str = "user", 
                 created_at: Optional[datetime] = None, user_id: Optional[str] = None):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.role = role
        self.created_at = created_at or datetime.now()
        self.user_id = user_id
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], user_id: str):
        """Firestore 문서에서 사용자 객체 생성"""
        return cls(
            username=data.get('username', ''),
            email=data.get('email'),
            hashed_password=data.get('hashed_password', ''),
            role=data.get('role', 'user'),
            created_at=data.get('created_at'),
            user_id=user_id
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """사용자 객체를 Firestore 문서로 변환"""
        return {
            'username': self.username,
            'email': self.email,
            'hashed_password': self.hashed_password,
            'role': self.role,
            'created_at': self.created_at
        }

# Firebase 기반 활동 로그 모델
class FirebaseActivityLog:
    def __init__(self, action: str, details: Optional[str] = None,
                 log_type: str = "user", log_level: str = "info",
                 user_id: Optional[str] = None, username: Optional[str] = None,
                 ip_address: Optional[str] = None, created_at: Optional[datetime] = None,
                 log_id: Optional[str] = None):
        self.action = action
        self.details = details
        self.log_type = log_type
        self.log_level = log_level
        self.user_id = user_id
        self.username = username
        self.ip_address = ip_address
        self.created_at = created_at or datetime.now()
        self.log_id = log_id
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], log_id: str):
        """Firestore 문서에서 로그 객체 생성"""
        return cls(
            action=data.get('action', ''),
            details=data.get('details'),
            log_type=data.get('log_type', 'user'),
            log_level=data.get('log_level', 'info'),
            user_id=data.get('user_id'),
            username=data.get('username'),
            ip_address=data.get('ip_address'),
            created_at=data.get('created_at'),
            log_id=log_id
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """로그 객체를 Firestore 문서로 변환"""
        return {
            'action': self.action,
            'details': self.details,
            'log_type': self.log_type,
            'log_level': self.log_level,
            'user_id': self.user_id,
            'username': self.username,
            'ip_address': self.ip_address,
            'created_at': self.created_at
        }

# Firebase 기반 AI 정보 모델
class FirebaseAIInfo:
    def __init__(self, date: str, info1_title: Optional[str] = None,
                 info1_content: Optional[str] = None, info1_terms: Optional[str] = None,
                 info2_title: Optional[str] = None, info2_content: Optional[str] = None,
                 info2_terms: Optional[str] = None, info3_title: Optional[str] = None,
                 info3_content: Optional[str] = None, info3_terms: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.date = date
        self.info1_title = info1_title
        self.info1_content = info1_content
        self.info1_terms = info1_terms
        self.info2_title = info2_title
        self.info2_content = info2_content
        self.info2_terms = info2_terms
        self.info3_title = info3_title
        self.info3_content = info3_content
        self.info3_terms = info3_terms
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Firestore 문서에서 AI 정보 객체 생성"""
        return cls(
            date=data.get('date', ''),
            info1_title=data.get('info1_title'),
            info1_content=data.get('info1_content'),
            info1_terms=data.get('info1_terms'),
            info2_title=data.get('info2_title'),
            info2_content=data.get('info2_content'),
            info2_terms=data.get('info2_terms'),
            info3_title=data.get('info3_title'),
            info3_content=data.get('info3_content'),
            info3_terms=data.get('info3_terms'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """AI 정보 객체를 Firestore 문서로 변환"""
        return {
            'date': self.date,
            'info1_title': self.info1_title,
            'info1_content': self.info1_content,
            'info1_terms': self.info1_terms,
            'info2_title': self.info2_title,
            'info2_content': self.info2_content,
            'info2_terms': self.info2_terms,
            'info3_title': self.info3_title,
            'info3_content': self.info3_content,
            'info3_terms': self.info3_terms,
            'created_at': self.created_at
        }

# Firebase 기반 사용자 진행 상황 모델
class FirebaseUserProgress:
    def __init__(self, session_id: str, date: str, learned_info: Optional[str] = None,
                 stats: Optional[str] = None, created_at: Optional[datetime] = None):
        self.session_id = session_id
        self.date = date
        self.learned_info = learned_info
        self.stats = stats
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Firestore 문서에서 사용자 진행 상황 객체 생성"""
        return cls(
            session_id=data.get('session_id', ''),
            date=data.get('date', ''),
            learned_info=data.get('learned_info'),
            stats=data.get('stats'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """사용자 진행 상황 객체를 Firestore 문서로 변환"""
        return {
            'session_id': self.session_id,
            'date': self.date,
            'learned_info': self.learned_info,
            'stats': self.stats,
            'created_at': self.created_at
        } 