# 네이버 뉴스 자동화 앱 (단순 버전)

네이버 뉴스에서 핫한 뉴스를 가져와 카카오톡으로 전송하는 간단한 자동화 앱입니다.

## 파일 구조 (최소화)

```
naver_news_automation/
├── key_setup.py          # API 키 설정 GUI
├── news_automation.py    # 메인 자동화 앱
├── keys.txt             # API 키 저장 파일 (자동 생성)
├── kakao_token.txt      # 카카오 토큰 저장 파일 (자동 생성)
├── requirements.txt     # 필요한 패키지
└── README.md           # 사용법
```

## 사용법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
```bash
python key_setup.py
```
- 네이버 API 키 입력
- 카카오 API 키 입력
- keys.txt 파일에 자동 저장

### 3. 앱 실행
```bash
python news_automation.py
```

### 4. 사용 순서
1. "API 키 설정" 버튼으로 키 입력
2. "카카오톡 인증" 버튼으로 인증
3. 뉴스 개수, 정렬 설정
4. 스케줄 설정 (간격/알람 모드)
5. "시작" 버튼으로 자동화 시작

## API 키 발급

### 네이버 API
1. [네이버 개발자센터](https://developers.naver.com) 접속
2. 애플리케이션 등록 → 검색 API 선택
3. Client ID, Client Secret 확인

### 카카오 API
1. [카카오 개발자센터](https://developers.kakao.com) 접속
2. 내 애플리케이션 → 앱 추가
3. 플랫폼: Web 추가 (http://localhost:8080)
4. 리다이렉트 URI: http://localhost:8080/callback
5. 카카오 로그인 활성화
6. 메시지 → 나에게 보내기 활성화
7. REST API 키 확인

## 기능

- ✅ 간단한 GUI (2개 파일만)
- ✅ API 키 txt 파일 저장
- ✅ 카카오톡 인증
- ✅ 네이버 뉴스 수집
- ✅ 스케줄링 (간격/알람 모드)
- ✅ 중복 방지
- ✅ 로그 표시

## 주의사항

- API 키는 안전하게 관리하세요
- 카카오 개발자센터에서 올바른 설정이 필요합니다
- 네이버/카카오 API 이용약관을 준수하세요
