# Railway 배포 가이드

## 프로젝트 URL
- **프론트엔드**: https://finance1-production.up.railway.app
- **백엔드**: https://mcp-hi.up.railway.app

## 환경변수 설정 방법

### 1. 프론트엔드 환경변수 설정

Railway 대시보드에서 프론트엔드 프로젝트로 이동 후:

1. **Variables** 탭 클릭
2. **New Variable** 버튼 클릭
3. 아래 변수들을 하나씩 추가:

```
NEXT_PUBLIC_API_URL=https://mcp-hi.up.railway.app
NEXT_PUBLIC_APP_NAME=AI Mastery Hub
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 2. 백엔드 환경변수 설정

Railway 대시보드에서 백엔드 프로젝트로 이동 후:

1. **Variables** 탭 클릭
2. **New Variable** 버튼 클릭
3. 아래 변수들을 하나씩 추가:

```
DATABASE_URL=postgresql://postgres.xazsbitfnpmfranrgfjw:rhdqngo123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
SECRET_KEY=your-secret-key-here
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=https://finance1-production.up.railway.app,http://localhost:3000
```

## 중요 사항

1. **SECRET_KEY**: 실제 배포 시에는 안전한 랜덤 문자열로 변경하세요
2. **DATABASE_URL**: 현재 Supabase 연결 문자열이 설정되어 있습니다
3. **CORS 설정**: 프론트엔드 URL이 백엔드의 ALLOWED_ORIGINS에 포함되어 있어야 합니다

## 배포 순서

1. 백엔드 먼저 배포 및 환경변수 설정
2. 프론트엔드 배포 및 환경변수 설정
3. 두 서비스 모두 정상 작동 확인

## 문제 해결

- 환경변수 설정 후에는 서비스를 재배포해야 합니다
- CORS 오류가 발생하면 ALLOWED_ORIGINS에 프론트엔드 URL이 정확히 포함되어 있는지 확인하세요
- API 연결 오류 시 NEXT_PUBLIC_API_URL이 올바른 백엔드 URL을 가리키는지 확인하세요 