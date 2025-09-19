#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 뉴스 자동화 앱
- 간단한 GUI로 스케줄 설정
- txt 파일에서 API 키 로드
- 카카오톡으로 뉴스 전송
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import schedule
import requests
import json
import webbrowser
import urllib.parse
from datetime import datetime
import os

class NewsAutomation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("네이버 뉴스 자동화")
        self.root.geometry("600x500")
        
        # API 키
        self.naver_id = ""
        self.naver_secret = ""
        self.kakao_key = ""
        
        # 카카오 인증
        self.access_token = None
        self.refresh_token = None
        
        # 스케줄링
        self.is_running = False
        self.scheduler_thread = None
        
        # 캐시 (간단한 리스트)
        self.sent_urls = []
        
        self.setup_ui()
        self.load_keys()
        
    def setup_ui(self):
        """GUI 설정"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="네이버 뉴스 자동화", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # API 키 설정 버튼
        key_frame = ttk.Frame(main_frame)
        key_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(key_frame, text="API 키 설정", command=self.open_key_setup).pack(side=tk.LEFT)
        self.key_status_label = ttk.Label(key_frame, text="API 키 미설정", foreground="red")
        self.key_status_label.pack(side=tk.RIGHT)
        
        # 카카오 인증
        auth_frame = ttk.Frame(main_frame)
        auth_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(auth_frame, text="카카오톡 인증", command=self.authenticate_kakao).pack(side=tk.LEFT)
        self.auth_status_label = ttk.Label(auth_frame, text="인증 필요", foreground="red")
        self.auth_status_label.pack(side=tk.RIGHT)
        
        # 뉴스 설정
        news_frame = ttk.LabelFrame(main_frame, text="뉴스 설정", padding="10")
        news_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(news_frame, text="개수:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.count_var = tk.StringVar(value="5")
        ttk.Spinbox(news_frame, from_=1, to=20, textvariable=self.count_var, width=5).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(news_frame, text="정렬:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.sort_var = tk.StringVar(value="최신")
        ttk.Combobox(news_frame, textvariable=self.sort_var, values=["최신", "관련도"], state="readonly", width=10).grid(row=0, column=3)
        
        # 스케줄 설정
        schedule_frame = ttk.LabelFrame(main_frame, text="스케줄 설정", padding="10")
        schedule_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 간격 모드
        self.mode_var = tk.StringVar(value="interval")
        ttk.Radiobutton(schedule_frame, text="간격 모드", variable=self.mode_var, value="interval").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(schedule_frame, text="알람 모드", variable=self.mode_var, value="alarm").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 간격 설정
        ttk.Label(schedule_frame, text="간격(시간):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.interval_var = tk.StringVar(value="1")
        ttk.Spinbox(schedule_frame, from_=1, to=24, textvariable=self.interval_var, width=5).grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(10, 0))
        
        # 알람 설정
        ttk.Label(schedule_frame, text="시간(예: 08:30,12:00,18:00):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.alarm_var = tk.StringVar(value="08:30,12:00,18:00")
        ttk.Entry(schedule_frame, textvariable=self.alarm_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=(10, 0))
        
        # 제어 버튼
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="시작", command=self.start_scheduler)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="중지", command=self.stop_scheduler, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="테스트 전송", command=self.test_send).pack(side=tk.LEFT)
        
        # 로그
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def load_keys(self):
        """keys.txt에서 API 키 로드"""
        try:
            if os.path.exists("keys.txt"):
                with open("keys.txt", 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('NAVER_ID='):
                            self.naver_id = line.split('=', 1)[1].strip()
                        elif line.startswith('NAVER_SECRET='):
                            self.naver_secret = line.split('=', 1)[1].strip()
                        elif line.startswith('KAKAO_KEY='):
                            self.kakao_key = line.split('=', 1)[1].strip()
                
                if self.naver_id and self.naver_secret and self.kakao_key:
                    self.key_status_label.config(text="API 키 설정됨", foreground="green")
                else:
                    self.key_status_label.config(text="API 키 불완전", foreground="orange")
            else:
                self.key_status_label.config(text="API 키 미설정", foreground="red")
        except Exception as e:
            self.log_message(f"키 로드 오류: {str(e)}")
    
    def open_key_setup(self):
        """API 키 설정 창 열기"""
        os.system("python key_setup.py")
        self.load_keys()  # 키 다시 로드
    
    def log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def authenticate_kakao(self):
        """카카오 인증"""
        if not self.kakao_key:
            messagebox.showwarning("경고", "먼저 API 키를 설정해주세요.")
            return
        
        try:
            self.log_message("카카오 인증 시작...")
            
            # 인증 URL 생성
            auth_url = "https://kauth.kakao.com/oauth/authorize"
            params = {
                'client_id': self.kakao_key,
                'redirect_uri': 'http://localhost:8080/callback',
                'response_type': 'code',
                'scope': 'talk_message'
            }
            
            auth_url_with_params = f"{auth_url}?{urllib.parse.urlencode(params)}"
            
            self.log_message("브라우저에서 카카오 로그인을 완료하세요...")
            webbrowser.open(auth_url_with_params)
            
            # 인증 코드 입력 받기
            code = tk.simpledialog.askstring("인증 코드", "리다이렉트된 URL에서 'code=' 뒤의 인증 코드를 입력하세요:")
            
            if code:
                # 토큰 요청
                token_url = "https://kauth.kakao.com/oauth/token"
                data = {
                    'grant_type': 'authorization_code',
                    'client_id': self.kakao_key,
                    'redirect_uri': 'http://localhost:8080/callback',
                    'code': code
                }
                
                response = requests.post(token_url, data=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data.get('access_token')
                    self.refresh_token = token_data.get('refresh_token')
                    
                    # 토큰 저장
                    with open("kakao_token.txt", 'w', encoding='utf-8') as f:
                        f.write(f"ACCESS_TOKEN={self.access_token}\n")
                        f.write(f"REFRESH_TOKEN={self.refresh_token}\n")
                    
                    self.auth_status_label.config(text="인증 완료", foreground="green")
                    self.log_message("카카오 인증 완료!")
                else:
                    self.log_message(f"인증 실패: {response.text}")
            else:
                self.log_message("인증 취소됨")
                
        except Exception as e:
            self.log_message(f"인증 오류: {str(e)}")
    
    def get_news(self):
        """네이버 뉴스 가져오기"""
        try:
            url = "https://openapi.naver.com/v1/search/news.json"
            headers = {
                "X-Naver-Client-Id": self.naver_id,
                "X-Naver-Client-Secret": self.naver_secret
            }
            
            params = {
                "query": "뉴스",
                "display": int(self.count_var.get()),
                "sort": "date" if self.sort_var.get() == "최신" else "sim"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                news_list = []
                
                for item in data.get("items", []):
                    # HTML 태그 제거
                    title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                    description = item.get("description", "").replace("<b>", "").replace("</b>", "")
                    link = item.get("link", "")
                    
                    news_list.append({
                        "title": title,
                        "description": description,
                        "link": link
                    })
                
                return news_list
            else:
                self.log_message(f"뉴스 API 오류: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_message(f"뉴스 가져오기 오류: {str(e)}")
            return []
    
    def send_to_kakao(self, message):
        """카카오톡으로 메시지 전송"""
        if not self.access_token:
            return False
        
        try:
            url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
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
            
            response = requests.post(url, headers=headers, data=data)
            return response.status_code == 200
            
        except Exception as e:
            self.log_message(f"카카오 전송 오류: {str(e)}")
            return False
    
    def send_news_job(self):
        """뉴스 전송 작업"""
        try:
            self.log_message("뉴스 전송 작업 시작...")
            
            # 뉴스 가져오기
            news_list = self.get_news()
            
            if not news_list:
                self.log_message("가져올 뉴스가 없습니다.")
                return
            
            # 중복 제거
            new_news = []
            for news in news_list:
                if news['link'] not in self.sent_urls:
                    new_news.append(news)
            
            if not new_news:
                self.log_message("새로운 뉴스가 없습니다.")
                return
            
            # 메시지 구성
            message = "🔥 오늘의 핫 뉴스\n\n"
            for i, news in enumerate(new_news[:5], 1):
                message += f"{i}. {news['title']}\n"
                if news['link']:
                    message += f"   링크: {news['link']}\n"
                message += "\n"
            
            # 카카오톡으로 전송
            if self.send_to_kakao(message):
                # 전송된 URL 캐시에 추가
                for news in new_news:
                    self.sent_urls.append(news['link'])
                
                self.log_message(f"뉴스 전송 완료: {len(new_news)}개")
            else:
                self.log_message("뉴스 전송 실패")
                
        except Exception as e:
            self.log_message(f"뉴스 전송 작업 오류: {str(e)}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if not self.access_token:
            messagebox.showwarning("경고", "먼저 카카오톡 인증을 완료해주세요.")
            return
        
        try:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            schedule.clear()
            
            if self.mode_var.get() == "interval":
                # 간격 모드
                interval = int(self.interval_var.get())
                schedule.every(interval).hours.do(self.send_news_job)
                self.log_message(f"간격 모드 시작: {interval}시간마다")
            else:
                # 알람 모드
                times = [t.strip() for t in self.alarm_var.get().split(",")]
                for time_str in times:
                    hour, minute = map(int, time_str.split(":"))
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.send_news_job)
                self.log_message(f"알람 모드 시작: {', '.join(times)}")
            
            # 스케줄러 스레드 시작
            self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            self.log_message("스케줄러 시작됨")
            
        except Exception as e:
            self.log_message(f"스케줄러 시작 오류: {str(e)}")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.is_running = False
        schedule.clear()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log_message("스케줄러 중지됨")
    
    def run_scheduler(self):
        """스케줄러 실행 루프"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def test_send(self):
        """테스트 전송"""
        if not self.access_token:
            messagebox.showwarning("경고", "먼저 카카오톡 인증을 완료해주세요.")
            return
        
        try:
            message = "🧪 테스트 메시지입니다.\n\n네이버 뉴스 자동화 앱이 정상 작동합니다."
            if self.send_to_kakao(message):
                self.log_message("테스트 전송 성공")
                messagebox.showinfo("성공", "테스트 메시지가 전송되었습니다.")
            else:
                self.log_message("테스트 전송 실패")
                messagebox.showerror("실패", "테스트 전송에 실패했습니다.")
        except Exception as e:
            self.log_message(f"테스트 전송 오류: {str(e)}")
    
    def run(self):
        """앱 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = NewsAutomation()
    app.run()
