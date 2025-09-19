@echo off
chcp 65001 >nul
title 네이버 뉴스 자동화 앱 정리

echo ========================================
echo    네이버 뉴스 자동화 앱 정리
echo ========================================
echo.

echo 🧹 불필요한 파일들을 정리합니다...
echo.

REM 빌드 파일 정리
if exist "build" (
    echo build 폴더를 삭제합니다...
    rmdir /s /q build
    echo ✅ build 폴더 삭제 완료
)

if exist "dist" (
    echo dist 폴더를 삭제합니다...
    rmdir /s /q dist
    echo ✅ dist 폴더 삭제 완료
)

REM Python 캐시 파일 정리
echo Python 캐시 파일을 정리합니다...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo ✅ Python 캐시 파일 정리 완료

REM 임시 파일 정리
echo 임시 파일을 정리합니다...
del /q *.tmp 2>nul
del /q *.log 2>nul
del /q *.spec 2>nul
echo ✅ 임시 파일 정리 완료

REM 설정 파일 정리 (선택사항)
echo.
echo 설정 파일을 정리하시겠습니까? (y/N)
echo - config.json (앱 설정)
echo - kakao_token.json (카카오 토큰)
echo - news_cache.json (뉴스 캐시)
set /p choice=
if /i "%choice%"=="y" (
    if exist "config.json" (
        del config.json
        echo ✅ config.json 삭제 완료
    )
    if exist "kakao_token.json" (
        del kakao_token.json
        echo ✅ kakao_token.json 삭제 완료
    )
    if exist "news_cache.json" (
        del news_cache.json
        echo ✅ news_cache.json 삭제 완료
    )
)

echo.
echo ========================================
echo    정리가 완료되었습니다!
echo ========================================
echo.
echo 정리된 항목:
echo - 빌드 파일 (build, dist)
echo - Python 캐시 파일
echo - 임시 파일
if /i "%choice%"=="y" (
    echo - 설정 파일
)
echo.
pause
