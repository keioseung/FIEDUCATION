# Railway CORS 오류 해결 가이드

## 현재 문제 상황
- **프론트엔드**: https://finance1-production.up.railway.app
- **백엔드**: https://mcp-hi.up.railway.app
- **오류**: 프론트엔드가 https://product2-production.up.railway.app로 요청하고 있음

## 해결 방법

### 1. 프론트엔드 환경변수 재설정

Railway 대시보드에서 프론트엔드 프로젝트로 이동:

1. **Variables** 탭 클릭
2. 기존 `NEXT_PUBLIC_API_URL` 변수가 있다면 삭제
3. **New Variable** 클릭하여 새로 추가:
   ```
   Key: NEXT_PUBLIC_API_URL
   Value: https://mcp-hi.up.railway.app
   ```
4. **Save** 클릭
5. **Deploy** 버튼 클릭하여 재배포

### 2. 백엔드 환경변수 확인

Railway 대시보드에서 백엔드 프로젝트로 이동:

1. **Variables** 탭에서 다음 변수들이 설정되어 있는지 확인:
       ```
    DATABASE_URL=postgresql://postgres.xazsbitfnpmfranrgfjw:rhdqngo123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
    SECRET_KEY=your-secret-key-here
    API_HOST=0.0.0.0
    API_PORT=8000
    ALLOWED_ORIGINS=https://finance1-production.up.railway.app,http://localhost:3000
    ```

### 3. 브라우저 캐시 클리어

1. 브라우저에서 `Ctrl + Shift + R` (하드 리프레시)
2. 또는 개발자 도구 > Network 탭 > "Disable cache" 체크
3. 브라우저 캐시 완전 삭제

### 4. 환경변수 확인 방법

프론트엔드에서 환경변수가 제대로 로드되었는지 확인:

1. 브라우저 개발자 도구 열기
2. Console 탭에서 다음 명령어 실행:
   ```javascript
   console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
   ```
3. 올바른 URL(`https://mcp-hi.up.railway.app`)이 출력되어야 함

### 5. 백엔드 CORS 설정 확인

백엔드가 올바르게 CORS를 처리하는지 확인:

1. 브라우저에서 직접 백엔드 URL 접속: https://mcp-hi.up.railway.app
2. JSON 응답이 나와야 함: `{"message": "AI Mastery Hub Backend is running", "status": "healthy", "version": "1.0.0"}`

### 6. 문제가 지속되는 경우

1. Railway에서 두 서비스 모두 재배포
2. 환경변수 설정 후 최소 5분 대기
3. 브라우저 캐시 완전 삭제 후 재시도

## 예상 결과

환경변수 설정이 완료되면:
- 프론트엔드가 올바른 백엔드 URL(`https://mcp-hi.up.railway.app`)로 요청
- CORS 오류 해결
- 로그인 기능 정상 작동 