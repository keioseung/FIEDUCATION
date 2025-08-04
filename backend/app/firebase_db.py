import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from typing import Optional

# Firebase 초기화 (한 번만 실행)
def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    try:
        print("🚀 Firebase 초기화 시작...")
        
        # 이미 초기화되었는지 확인
        if firebase_admin._apps:
            print("ℹ️ Firebase Admin SDK가 이미 초기화되어 있습니다")
            return True
        
        # 환경변수에서 서비스 계정 키 읽기 시도
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        if service_account_json:
            try:
                service_account_info = json.loads(service_account_json)
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin SDK 초기화 완료 (환경변수)")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ Firebase 서비스 계정 JSON 파싱 실패: {e}")
                return False
        
        # 파일에서 읽기 시도 (여러 가능한 경로)
        possible_paths = [
            '/app/firebase-service-account.json',  # Railway 컨테이너 경로
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'firebase-service-account.json'),
            './firebase-service-account.json',
            'firebase-service-account.json',
            '/tmp/firebase-service-account.json'
        ]
        
        for service_account_path in possible_paths:
            print(f"🔍 경로 확인 중: {service_account_path}")
            if os.path.exists(service_account_path):
                try:
                    print(f"✅ 파일 발견: {service_account_path}")
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    print(f"✅ Firebase Admin SDK 초기화 완료 (파일: {service_account_path})")
                    return True
                except Exception as e:
                    print(f"❌ Firebase 초기화 실패 (파일: {service_account_path}): {e}")
                    continue
        
        print("❌ Firebase 서비스 계정 키를 찾을 수 없습니다")
        print("가능한 해결책:")
        print("1. Railway 환경변수에 FIREBASE_SERVICE_ACCOUNT 설정")
        print("2. firebase-service-account.json 파일을 Railway Files에 업로드")
        return False
        
    except Exception as e:
        print(f"❌ Firebase 초기화 실패: {e}")
        print(f"🔍 에러 타입: {type(e)}")
        import traceback
        print(f"📋 상세 에러: {traceback.format_exc()}")
        return False

# Firestore 클라이언트 가져오기
def get_firestore_client():
    """Firestore 클라이언트 반환"""
    try:
        if not firebase_admin._apps:
            initialize_firebase()
        return firestore.client()
    except Exception as e:
        print(f"❌ Firestore 클라이언트 생성 실패: {e}")
        return None

# 데이터베이스 연결 테스트
def test_connection():
    """Firebase 연결 테스트"""
    try:
        db = get_firestore_client()
        if db:
            # 간단한 쿼리로 연결 테스트
            test_doc = db.collection('test').document('connection_test')
            test_doc.set({'status': 'connected', 'timestamp': firestore.SERVER_TIMESTAMP})
            test_doc.delete()  # 테스트 문서 삭제
            print("✅ Firebase 연결 성공")
            return True
        return False
    except Exception as e:
        print(f"❌ Firebase 연결 테스트 실패: {e}")
        return False

# 컬렉션 참조 가져오기
def get_collection(collection_name: str):
    """특정 컬렉션 참조 반환"""
    try:
        db = get_firestore_client()
        if db:
            return db.collection(collection_name)
        return None
    except Exception as e:
        print(f"❌ 컬렉션 참조 생성 실패: {e}")
        return None

# 문서 참조 가져오기
def get_document(collection_name: str, document_id: str):
    """특정 문서 참조 반환"""
    try:
        db = get_firestore_client()
        if db:
            return db.collection(collection_name).document(document_id)
        return None
    except Exception as e:
        print(f"❌ 문서 참조 생성 실패: {e}")
        return None 