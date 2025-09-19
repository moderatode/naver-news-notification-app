#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카카오톡 나에게 보내기 API 연동 모듈
- 카카오 OAuth 2.0 인증
- 나에게 보내기 메시지 전송
- 토큰 자동 갱신
"""

import requests
import json
import os
import webbrowser
import urllib.parse
from typing import Optional, Dict
import time
from datetime import datetime, timedelta

class KakaoAPI:
    def __init__(self):
        # 카카오 API 설정
        from api_keys import KAKAO_CLIENT_ID
        self.client_id = KAKAO_CLIENT_ID
        self.redirect_uri = "http://localhost:8080/callback"  # 리다이렉트 URI
        self.base_url = "https://kauth.kakao.com"
        self.api_url = "https://kapi.kakao.com"
        
        # 토큰 저장 파일
        self.token_file = "kakao_token.json"
        
        # 인증 상태
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # 토큰 로드
        self._load_token()
    
    def _load_token(self):
        """저장된 토큰 로드"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                    self.access_token = token_data.get('access_token')
                    self.refresh_token = token_data.get('refresh_token')
                    self.token_expires_at = token_data.get('expires_at')
                    
                    # 토큰 만료 체크
                    if self.token_expires_at and datetime.now().timestamp() >= self.token_expires_at:
                        self._refresh_token()
        except Exception as e:
            print(f"토큰 로드 오류: {str(e)}")
    
    def _save_token(self):
        """토큰 저장"""
        try:
            token_data = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_at': self.token_expires_at
            }
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"토큰 저장 오류: {str(e)}")
    
    def _refresh_token(self):
        """토큰 갱신"""
        if not self.refresh_token:
            return False
        
        try:
            url = f"{self.base_url}/oauth/token"
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'refresh_token': self.refresh_token
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token', self.refresh_token)
                self.token_expires_at = time.time() + token_data.get('expires_in', 3600)
                self._save_token()
                return True
            else:
                print(f"토큰 갱신 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"토큰 갱신 오류: {str(e)}")
            return False
    
    def authenticate(self) -> bool:
        """
        카카오 OAuth 인증
        
        Returns:
            인증 성공 여부
        """
        try:
            # 1단계: 인증 코드 요청
            auth_url = f"{self.base_url}/oauth/authorize"
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': 'talk_message'
            }
            
            auth_url_with_params = f"{auth_url}?{urllib.parse.urlencode(params)}"
            
            print("카카오 인증을 위해 브라우저가 열립니다...")
            print(f"인증 URL: {auth_url_with_params}")
            
            # 브라우저 열기
            webbrowser.open(auth_url_with_params)
            
            # 사용자로부터 인증 코드 입력 받기
            print("\n브라우저에서 카카오 계정으로 로그인하고, 인증을 완료한 후")
            print("리다이렉트된 URL에서 'code=' 뒤의 인증 코드를 복사해서 입력해주세요.")
            print("예: http://localhost:8080/callback?code=인증코드")
            
            auth_code = input("인증 코드를 입력하세요: ").strip()
            
            if not auth_code:
                print("인증 코드가 입력되지 않았습니다.")
                return False
            
            # 2단계: 액세스 토큰 요청
            return self._get_access_token(auth_code)
            
        except Exception as e:
            print(f"인증 오류: {str(e)}")
            return False
    
    def _get_access_token(self, auth_code: str) -> bool:
        """인증 코드로 액세스 토큰 획득"""
        try:
            url = f"{self.base_url}/oauth/token"
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'code': auth_code
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                self.token_expires_at = time.time() + token_data.get('expires_in', 3600)
                self._save_token()
                
                print("카카오 인증이 완료되었습니다!")
                return True
            else:
                print(f"토큰 획득 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"토큰 획득 오류: {str(e)}")
            return False
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        if not self.access_token:
            return False
        
        # 토큰 만료 체크
        if self.token_expires_at and datetime.now().timestamp() >= self.token_expires_at:
            return self._refresh_token()
        
        return True
    
    def send_message(self, message: str) -> bool:
        """
        나에게 보내기 메시지 전송
        
        Args:
            message: 전송할 메시지
        
        Returns:
            전송 성공 여부
        """
        if not self.is_authenticated():
            print("카카오 인증이 필요합니다.")
            return False
        
        try:
            url = f"{self.api_url}/v2/api/talk/memo/default/send"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'template_object': json.dumps({
                    'object_type': 'text',
                    'text': message,
                    'link': {
                        'web_url': 'https://news.naver.com',
                        'mobile_web_url': 'https://news.naver.com'
                    }
                })
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                print("메시지 전송 성공")
                return True
            else:
                print(f"메시지 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"메시지 전송 오류: {str(e)}")
            return False
    
    def send_news_message(self, news_list: list) -> bool:
        """
        뉴스 리스트를 카카오톡으로 전송
        
        Args:
            news_list: 뉴스 리스트
        
        Returns:
            전송 성공 여부
        """
        if not news_list:
            return False
        
        try:
            # 메시지 구성
            message_parts = ["🔥 오늘의 핫 뉴스"]
            
            for i, news in enumerate(news_list[:5], 1):  # 최대 5개
                title = news.get('title', '')[:50]  # 제목 길이 제한
                link = news.get('link', '')
                
                message_parts.append(f"\n{i}. {title}")
                if link:
                    message_parts.append(f"   링크: {link}")
            
            message = "\n".join(message_parts)
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"뉴스 메시지 전송 오류: {str(e)}")
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """사용자 정보 가져오기"""
        if not self.is_authenticated():
            return None
        
        try:
            url = f"{self.api_url}/v2/user/me"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"사용자 정보 가져오기 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"사용자 정보 가져오기 오류: {str(e)}")
            return None
    
    def logout(self):
        """로그아웃 (토큰 삭제)"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            
            self.access_token = None
            self.refresh_token = None
            self.token_expires_at = None
            
            print("카카오 로그아웃이 완료되었습니다.")
            
        except Exception as e:
            print(f"로그아웃 오류: {str(e)}")
    
    def test_connection(self) -> bool:
        """연결 테스트"""
        try:
            if not self.is_authenticated():
                return False
            
            # 사용자 정보 가져오기로 연결 테스트
            user_info = self.get_user_info()
            return user_info is not None
            
        except Exception as e:
            print(f"연결 테스트 오류: {str(e)}")
            return False

# 간단한 인증 코드 서버 (개발용)
class AuthCodeServer:
    def __init__(self, port: int = 8080):
        self.port = port
        self.auth_code = None
        self.server = None
    
    def start_server(self):
        """인증 코드 서버 시작"""
        try:
            import http.server
            import socketserver
            import threading
            
            class AuthHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path.startswith('/callback'):
                        # 인증 코드 추출
                        query = urllib.parse.urlparse(self.path).query
                        params = urllib.parse.parse_qs(query)
                        code = params.get('code', [None])[0]
                        
                        if code:
                            self.server.auth_code = code
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html; charset=utf-8')
                            self.end_headers()
                            self.wfile.write(b'''
                            <html>
                            <head><title>인증 완료</title></head>
                            <body>
                                <h1>인증이 완료되었습니다!</h1>
                                <p>이 창을 닫고 앱으로 돌아가세요.</p>
                            </body>
                            </html>
                            ''')
                        else:
                            self.send_response(400)
                            self.end_headers()
                            self.wfile.write(b'인증 코드를 찾을 수 없습니다.')
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def log_message(self, format, *args):
                    pass  # 로그 메시지 비활성화
            
            self.server = socketserver.TCPServer(("", self.port), AuthHandler)
            self.server.auth_code = None
            
            # 서버를 별도 스레드에서 실행
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return True
            
        except Exception as e:
            print(f"인증 서버 시작 오류: {str(e)}")
            return False
    
    def stop_server(self):
        """인증 서버 중지"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def get_auth_code(self, timeout: int = 60) -> Optional[str]:
        """인증 코드 가져오기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.server and self.server.auth_code:
                return self.server.auth_code
            time.sleep(0.1)
        return None
