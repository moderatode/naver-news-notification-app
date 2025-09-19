@echo off
chcp 65001 >nul
title 네이버 뉴스 자동화 앱 빌드

echo ========================================
echo    네이버 뉴스 자동화 앱 빌드
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

REM 가상환경 활성화
if exist "venv" (
    echo 🔄 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  가상환경이 없습니다. setup.bat을 먼저 실행해주세요.
    pause
    exit /b 1
)

REM PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 PyInstaller를 설치합니다...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller 설치에 실패했습니다.
        pause
        exit /b 1
    )
)

REM API 키 파일 확인
if not exist "api_keys.py" (
    echo ❌ API 키 파일이 없습니다.
    echo api_keys.py 파일을 생성하고 API 키를 설정해주세요.
    pause
    exit /b 1
)

REM 빌드 실행
echo 🔨 실행 파일을 빌드합니다...
echo 이 과정은 몇 분이 걸릴 수 있습니다...
echo.

python build.py
if errorlevel 1 (
    echo ❌ 빌드에 실패했습니다.
    pause
    exit /b 1
)

REM 빌드 결과 확인
if exist "dist\네이버뉴스자동화.exe" (
    echo.
    echo ✅ 빌드가 완료되었습니다!
    echo 실행 파일 위치: dist\네이버뉴스자동화.exe
    echo.
    echo 실행 파일을 다른 컴퓨터로 복사하여 사용할 수 있습니다.
    echo.
    echo 실행 파일을 지금 실행하시겠습니까? (y/N)
    set /p choice=
    if /i "%choice%"=="y" (
        start "" "dist\네이버뉴스자동화.exe"
    )
) else (
    echo ❌ 빌드된 실행 파일을 찾을 수 없습니다.
)

echo.
pause
