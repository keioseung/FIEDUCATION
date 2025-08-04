# CORS 오류 디버깅 가이드

## 현재 오류 분석
- **오류 타입**: CORS error (preflight 404)
- **원인**: 프론트엔드가 여전히 잘못된 백엔드 URL로 요청
- **예상 URL**: https://product2-production.up.railway.app (잘못된 URL)
- **올바른 URL**: https://mcp-hi.up.railway.app

## 즉시 해결 방법

### 1. Railway 환경변수 강제 재설정

#### 프론트엔드 (finance1-production.up.railway.app)
1. Railway 대시보드 → 프론트엔드 프로젝트
2. **Variables** 탭
3. 기존 `NEXT_PUBLIC_API_URL` 변수가 있다면 **삭제**
4. **New Variable** 클릭
5. 설정:
   ```
   Key: NEXT_PUBLIC_API_URL
   Value: https://mcp-hi.up.railway.app
   ```
6. **Save** 클릭
7. **Deploy** 버튼 클릭 (재배포 필수!)

#### 백엔드 (mcp-hi.up.railway.app)
1. Railway 대시보드 → 백엔드 프로젝트
2. **Variables** 탭
3. 다음 변수들이 정확히 설정되어 있는지 확인:
   ```
   DATABASE_URL=postgresql://postgres.xazsbitfnpmfranrgfjw:rhdqngo123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   SECRET_KEY=your-secret-key-here
   API_HOST=0.0.0.0
   API_PORT=8000
   ALLOWED_ORIGINS=https://finance1-production.up.railway.app,http://localhost:3000
   ```
4. **Deploy** 버튼 클릭

### 2. 브라우저 캐시 완전 삭제

1. **Chrome/Edge**:
   - `Ctrl + Shift + Delete`
   - 시간 범위: "전체 기간"
   - 체크박스 모두 선택
   - "데이터 삭제" 클릭

2. **하드 리프레시**:
   - `Ctrl + Shift + R`
   - 또는 `F12` → Network 탭 → "Disable cache" 체크

### 3. 환경변수 확인

브라우저 개발자 도구에서 확인:

1. `F12` → Console 탭
2. 다음 명령어 실행:
   ```javascript
   console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
   ```
3. **예상 결과**: `https://mcp-hi.up.railway.app`
4. **잘못된 결과**: `undefined` 또는 다른 URL

### 4. 백엔드 직접 테스트

브라우저에서 직접 백엔드 URL 접속:
```
https://mcp-hi.up.railway.app
```

**예상 응답**:
```json
{
  "message": "AI Mastery Hub Backend is running",
  "status": "healthy",
  "version": "1.0.0"
}
```

### 5. Railway 배포 상태 확인

1. Railway 대시보드에서 두 서비스 모두 **"Deployed"** 상태인지 확인
2. 배포 로그에서 오류가 없는지 확인
3. 환경변수가 제대로 적용되었는지 확인

## 문제가 지속되는 경우

### 대안 1: 프론트엔드 하드코딩 (임시)
프론트엔드 코드에서 직접 API URL을 설정:

```typescript
// frontend/src/lib/api.ts
const API_BASE_URL = 'https://mcp-hi.up.railway.app'  // 하드코딩
```

### 대안 2: Railway 프로젝트 재생성
1. 기존 프로젝트 삭제
2. 새로 프로젝트 생성
3. 환경변수 설정 후 배포

### 대안 3: 다른 배포 플랫폼 사용
- Vercel (프론트엔드)
- Render (백엔드)
- Heroku

## 예상 해결 시간
- 환경변수 설정: 5-10분
- 재배포: 5-10분
- 캐시 삭제: 즉시
- **총 예상 시간**: 15-20분

## 성공 확인 방법
1. 브라우저 개발자 도구에서 CORS 오류 없음
2. 로그인 기능 정상 작동
3. API 요청이 올바른 URL로 전송됨 