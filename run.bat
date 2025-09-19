@echo off
chcp 65001 >nul
title 네이버 뉴스 자동화 앱

echo ========================================
echo    네이버 뉴스 자동화 앱 실행
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

REM 가상환경 확인 및 생성
if not exist "venv" (
    echo 📦 가상환경을 생성합니다...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
)

REM 가상환경 활성화
echo 🔄 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

REM 의존성 설치
echo 📥 필요한 패키지를 설치합니다...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치에 실패했습니다.
    pause
    exit /b 1
)

REM API 키 파일 확인
if not exist "api_keys.py" (
    echo ⚠️  API 키 파일이 없습니다.
    echo api_keys.py.example을 api_keys.py로 복사하고 API 키를 설정해주세요.
    echo.
    echo 계속하시겠습니까? (y/N)
    set /p choice=
    if /i not "%choice%"=="y" (
        echo 취소되었습니다.
        pause
        exit /b 0
    )
)

REM 앱 실행
echo 🚀 네이버 뉴스 자동화 앱을 시작합니다...
echo.
python main.py

REM 오류 발생 시
if errorlevel 1 (
    echo.
    echo ❌ 앱 실행 중 오류가 발생했습니다.
    echo 오류를 확인하고 다시 시도해주세요.
    pause
)

echo.
echo 앱이 종료되었습니다.
pause
