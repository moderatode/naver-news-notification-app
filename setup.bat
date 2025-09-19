@echo off
chcp 65001 >nul
title 네이버 뉴스 자동화 앱 설정

echo ========================================
echo    네이버 뉴스 자동화 앱 초기 설정
echo ========================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python 3.8 이상을 설치해주세요.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python이 설치되어 있습니다.

REM 가상환경 생성
echo 📦 가상환경을 생성합니다...
if exist "venv" (
    echo 기존 가상환경을 삭제합니다...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo ❌ 가상환경 생성에 실패했습니다.
    pause
    exit /b 1
)

echo ✅ 가상환경이 생성되었습니다.

REM 가상환경 활성화
echo 🔄 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

REM pip 업그레이드
echo 📥 pip을 업그레이드합니다...
python -m pip install --upgrade pip

REM 의존성 설치
echo 📦 필요한 패키지를 설치합니다...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치에 실패했습니다.
    pause
    exit /b 1
)

echo ✅ 패키지 설치가 완료되었습니다.

REM API 키 파일 설정
echo.
echo 🔑 API 키 설정을 도와드립니다...
if not exist "api_keys.py" (
    if exist "api_keys.py.example" (
        echo api_keys.py.example을 api_keys.py로 복사합니다...
        copy "api_keys.py.example" "api_keys.py"
        echo ✅ api_keys.py 파일이 생성되었습니다.
        echo.
        echo ⚠️  중요: api_keys.py 파일을 열어서 실제 API 키를 입력해주세요!
        echo.
        echo API 키 발급 방법:
        echo 1. 네이버 개발자센터: https://developers.naver.com
        echo 2. 카카오 개발자센터: https://developers.kakao.com
        echo.
        pause
    ) else (
        echo ❌ api_keys.py.example 파일을 찾을 수 없습니다.
        pause
        exit /b 1
    )
) else (
    echo ✅ api_keys.py 파일이 이미 존재합니다.
)

REM Git 초기화 (선택사항)
echo.
echo 📚 Git 저장소를 초기화하시겠습니까? (y/N)
set /p git_choice=
if /i "%git_choice%"=="y" (
    git init
    git add .
    git commit -m "Initial commit: 네이버 뉴스 자동화 앱 설정 완료"
    echo ✅ Git 저장소가 초기화되었습니다.
)

echo.
echo ========================================
echo    설정이 완료되었습니다!
echo ========================================
echo.
echo 다음 단계:
echo 1. api_keys.py 파일에서 API 키를 설정하세요
echo 2. run.bat 파일을 더블클릭하여 앱을 실행하세요
echo.
echo API 키 발급 방법:
echo - 네이버: https://developers.naver.com
echo - 카카오: https://developers.kakao.com
echo.
pause
