# 네이버 뉴스 자동화 앱

네이버 뉴스에서 가장 핫한 토픽 5개 뉴스를 자동으로 가져와 카카오톡 "나에게 보내기"로 전송하는 자동화 앱입니다.

## 주요 기능

- 🔥 **핫한 뉴스 자동 수집**: 네이버 공식 뉴스 검색 API를 사용하여 실시간 핫한 뉴스 수집
- 📱 **카카오톡 자동 전송**: 카카오톡 "나에게 보내기" API를 통한 자동 메시지 전송
- ⏰ **스케줄링**: 간격 모드(매 N시간) 또는 알람 모드(지정 시각) 지원
- 🔄 **OAuth 자동 관리**: 카카오 OAuth 토큰 자동 갱신
- 🚫 **중복 방지**: 로컬 캐시를 통한 중복 기사 전송 방지
- 🎛️ **GUI 설정**: 사용자 친화적인 GUI 인터페이스
- 💾 **설정 저장**: 로컬 설정 파일로 설정 유지

## 설치 및 실행

### 1. 필수 요구사항

- Python 3.8 이상
- 네이버 개발자센터 API 키
- 카카오 개발자센터 API 키

### 2. 설치

```bash
# 저장소 클론
git clone <repository-url>
cd naver_news_automation

# 의존성 설치
pip install -r requirements.txt
```

### 3. API 키 설정

1. `api_keys.py` 파일을 열어서 API 키를 설정합니다:

```python
# 네이버 뉴스 검색 API 키
NAVER_CLIENT_ID = "YOUR_NAVER_CLIENT_ID"
NAVER_CLIENT_SECRET = "YOUR_NAVER_CLIENT_SECRET"

# 카카오톡 API 키
KAKAO_CLIENT_ID = "YOUR_KAKAO_CLIENT_ID"
```

2. **네이버 API 키 발급**:
   - [네이버 개발자센터](https://developers.naver.com) 접속
   - 로그인 후 "Application" > "애플리케이션 등록"
   - 애플리케이션 이름, 사용 API 선택 (검색 API)
   - 등록 후 Client ID, Client Secret 확인

3. **카카오 API 키 발급**:
   - [카카오 개발자센터](https://developers.kakao.com) 접속
   - 로그인 후 "내 애플리케이션" > "애플리케이션 추가"
   - 앱 이름, 플랫폼 설정
   - "제품 설정" > "카카오 로그인" 활성화
   - "제품 설정" > "메시지" > "나에게 보내기" 활성화
   - "앱 키"에서 REST API 키 확인

### 4. 실행

```bash
python main.py
```

## 사용법

### 1. 카카오톡 인증

앱을 실행한 후 "카카오톡 인증" 버튼을 클릭하여 OAuth 인증을 완료합니다.

### 2. 뉴스 설정

- **표시 개수**: 가져올 뉴스 개수 (1-20개)
- **정렬**: 최신순 또는 관련도순

### 3. 스케줄 설정

#### 간격 모드
- 매 N시간마다 뉴스를 가져와 전송
- 1-24시간 간격 설정 가능

#### 알람 모드
- 지정된 시각에 뉴스를 가져와 전송
- 여러 시각 설정 가능 (예: 08:30,12:00,18:00)
- 요일 선택 가능 (평일/주말/특정 요일)

### 4. 시작/중지

- **시작**: 설정된 스케줄에 따라 자동 실행 시작
- **중지**: 자동 실행 중지
- **테스트 전송**: 현재 설정으로 테스트 메시지 전송

## 파일 구조

```
naver_news_automation/
├── main.py                 # 메인 GUI 애플리케이션
├── news_api.py            # 네이버 뉴스 API 연동
├── kakao_api.py           # 카카오톡 API 연동
├── cache_manager.py       # 중복 방지 캐시 관리
├── config_manager.py     # 설정 관리
├── api_keys.py           # API 키 설정
├── requirements.txt      # 의존성 패키지
├── .gitignore           # Git 무시 파일
└── README.md           # 사용법 설명
```

## 주요 모듈

### NewsAutomationApp (main.py)
- GUI 인터페이스 관리
- 스케줄링 로직
- 사용자 설정 관리

### NaverNewsAPI (news_api.py)
- 네이버 뉴스 검색 API 연동
- 핫한 뉴스 수집
- 뉴스 데이터 정제

### KakaoAPI (kakao_api.py)
- 카카오 OAuth 인증
- 나에게 보내기 메시지 전송
- 토큰 자동 갱신

### CacheManager (cache_manager.py)
- 전송된 뉴스 URL 캐시 관리
- 중복 방지 로직
- 캐시 정리 및 최적화

### ConfigManager (config_manager.py)
- 앱 설정 저장/로드
- JSON 기반 설정 관리
- 설정 유효성 검사

## 설정 파일

### config.json
앱 설정이 저장되는 파일입니다:
```json
{
  "count": 5,
  "sort": "최신",
  "schedule_mode": "interval",
  "interval": 1,
  "alarm_times": "08:30,12:00,18:00",
  "weekdays": {
    "월": true,
    "화": true,
    "수": true,
    "목": true,
    "금": true,
    "토": false,
    "일": false
  }
}
```

### kakao_token.json
카카오 OAuth 토큰이 저장되는 파일입니다 (자동 생성).

### news_cache.json
전송된 뉴스 URL 캐시가 저장되는 파일입니다 (자동 생성).

## 문제 해결

### 1. API 키 오류
- 네이버/카카오 API 키가 올바르게 설정되었는지 확인
- API 키 발급 상태 및 권한 확인

### 2. 인증 오류
- 카카오톡 인증을 다시 시도
- 토큰 파일 삭제 후 재인증

### 3. 뉴스 수집 실패
- 네이버 API 사용량 제한 확인
- 인터넷 연결 상태 확인

### 4. 메시지 전송 실패
- 카카오톡 앱에서 "나에게 보내기" 기능 활성화 확인
- 토큰 만료 시 자동 갱신 확인

## 라이선스

이 프로젝트는 개인 사용을 위한 오픈소스 프로젝트입니다.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 주의사항

- 네이버와 카카오의 API 이용약관을 준수해주세요
- API 사용량 제한을 확인하고 적절히 사용해주세요
- 개인정보 보호를 위해 API 키를 안전하게 관리해주세요
