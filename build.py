#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실행 파일 빌드 스크립트
- PyInstaller를 사용하여 단일 실행 파일 생성
- Windows 환경에 최적화
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """실행 파일 빌드"""
    try:
        print("네이버 뉴스 자동화 앱 빌드를 시작합니다...")
        
        # PyInstaller 명령어 구성
        cmd = [
            "pyinstaller",
            "--onefile",                    # 단일 실행 파일
            "--windowed",                   # 콘솔 창 숨김
            "--name=네이버뉴스자동화",        # 실행 파일 이름
            "--icon=icon.ico",              # 아이콘 (있는 경우)
            "--add-data=api_keys.py;.",    # API 키 파일 포함
            "--hidden-import=tkinter",      # tkinter 명시적 포함
            "--hidden-import=schedule",     # schedule 모듈 포함
            "--hidden-import=pytz",        # pytz 모듈 포함
            "--hidden-import=requests",     # requests 모듈 포함
            "--hidden-import=json",         # json 모듈 포함
            "--hidden-import=threading",    # threading 모듈 포함
            "--hidden-import=datetime",     # datetime 모듈 포함
            "--hidden-import=time",         # time 모듈 포함
            "--hidden-import=os",          # os 모듈 포함
            "--hidden-import=webbrowser",  # webbrowser 모듈 포함
            "--hidden-import=urllib.parse", # urllib.parse 모듈 포함
            "--hidden-import=hashlib",      # hashlib 모듈 포함
            "--hidden-import=re",          # re 모듈 포함
            "--hidden-import=bs4",         # beautifulsoup4 모듈 포함
            "--hidden-import=lxml",        # lxml 모듈 포함
            "--clean",                      # 이전 빌드 정리
            "main.py"                       # 메인 파일
        ]
        
        # 아이콘 파일이 없으면 아이콘 옵션 제거
        if not os.path.exists("icon.ico"):
            cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        
        print("PyInstaller 명령어 실행 중...")
        print(" ".join(cmd))
        
        # PyInstaller 실행
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 빌드가 성공적으로 완료되었습니다!")
            print(f"실행 파일 위치: dist/네이버뉴스자동화.exe")
            
            # 빌드 결과 확인
            exe_path = Path("dist/네이버뉴스자동화.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"파일 크기: {size_mb:.1f} MB")
            
            return True
        else:
            print("❌ 빌드 실패!")
            print("오류 출력:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 빌드 중 오류 발생: {str(e)}")
        return False

def clean_build_files():
    """빌드 파일 정리"""
    try:
        print("빌드 파일을 정리합니다...")
        
        # 정리할 디렉토리들
        dirs_to_clean = ["build", "__pycache__"]
        files_to_clean = ["*.spec"]
        
        # 디렉토리 정리
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"삭제됨: {dir_name}")
        
        # spec 파일 정리
        for spec_file in Path(".").glob("*.spec"):
            spec_file.unlink()
            print(f"삭제됨: {spec_file}")
        
        print("✅ 빌드 파일 정리 완료")
        
    except Exception as e:
        print(f"빌드 파일 정리 중 오류: {str(e)}")

def create_installer():
    """설치 프로그램 생성 (선택사항)"""
    try:
        print("설치 프로그램 생성을 시도합니다...")
        
        # NSIS 스크립트 생성
        nsis_script = """
!define APP_NAME "네이버 뉴스 자동화"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "개발자"
!define APP_EXE "네이버뉴스자동화.exe"

Name "${APP_NAME}"
OutFile "네이버뉴스자동화_설치프로그램.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"
InstallDirRegKey HKLM "Software\\${APP_NAME}" "Install_Dir"

Section "Main"
    SetOutPath "$INSTDIR"
    File "dist\\${APP_EXE}"
    File "README.md"
    File "requirements.txt"
    
    CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    CreateShortCut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
    
    WriteRegStr HKLM "Software\\${APP_NAME}" "Install_Dir" "$INSTDIR"
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\${APP_EXE}"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\requirements.txt"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\\${APP_NAME}"
    Delete "$DESKTOP\\${APP_NAME}.lnk"
    
    DeleteRegKey HKLM "Software\\${APP_NAME}"
SectionEnd
"""
        
        with open("installer.nsi", "w", encoding="utf-8") as f:
            f.write(nsis_script)
        
        print("✅ NSIS 스크립트가 생성되었습니다: installer.nsi")
        print("NSIS가 설치되어 있다면 다음 명령어로 설치 프로그램을 생성할 수 있습니다:")
        print("makensis installer.nsi")
        
    except Exception as e:
        print(f"설치 프로그램 생성 중 오류: {str(e)}")

def main():
    """메인 함수"""
    print("=" * 50)
    print("네이버 뉴스 자동화 앱 빌드 도구")
    print("=" * 50)
    
    # PyInstaller 설치 확인
    try:
        subprocess.run(["pyinstaller", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller가 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요: pip install pyinstaller")
        return
    
    # 빌드 실행
    if build_executable():
        print("\n" + "=" * 50)
        print("빌드 완료!")
        print("=" * 50)
        print("실행 파일: dist/네이버뉴스자동화.exe")
        print("이 파일을 다른 컴퓨터로 복사하여 실행할 수 있습니다.")
        print("\n주의사항:")
        print("- API 키가 포함되어 있으므로 안전하게 관리하세요.")
        print("- 최초 실행 시 카카오톡 인증이 필요합니다.")
        print("- Windows Defender에서 차단될 수 있으니 예외 처리하세요.")
        
        # 빌드 파일 정리 옵션
        response = input("\n빌드 파일을 정리하시겠습니까? (y/N): ")
        if response.lower() in ['y', 'yes']:
            clean_build_files()
        
        # 설치 프로그램 생성 옵션
        response = input("\n설치 프로그램을 생성하시겠습니까? (y/N): ")
        if response.lower() in ['y', 'yes']:
            create_installer()
    
    else:
        print("\n❌ 빌드에 실패했습니다.")
        print("오류를 확인하고 다시 시도해주세요.")

if __name__ == "__main__":
    main()
