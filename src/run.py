#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 뉴스 자동화 앱
- 간단한 GUI로 스케줄 설정
- txt 파일에서 API 키 로드
- 카카오톡으로 뉴스 전송
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
import time
import schedule
import requests
import json
import webbrowser
import urllib.parse
from datetime import datetime
import os
import html

class NewsAutomation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📰 네이버 뉴스 알림 어플리케이션")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 화면 중앙에 배치
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
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
        
        # config 폴더가 없으면 생성 (상위 디렉토리에)
        os.makedirs("../config", exist_ok=True)
        
        self.setup_ui()
        self.load_keys()
        self.load_kakao_token()  # 카카오톡 토큰 로드
        self.on_sort_change()  # 초기 상태 설정
        self.on_mode_change()  # 초기 모드 설정
        
    def setup_ui(self):
        """GUI 설정"""
        # 스크롤 가능한 캔버스 생성
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 메인 프레임
        main_frame = ttk.Frame(scrollable_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바와 캔버스 배치
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 마우스 휠 바인딩
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 제목
        title_label = ttk.Label(main_frame, text="📰 네이버 뉴스 알림 어플리케이션", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # API 키 설정 버튼
        key_frame = ttk.Frame(main_frame)
        key_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(key_frame, text="API 키 설정", command=self.open_key_setup).pack(side=tk.LEFT, padx=(0, 10))
        self.key_status_label = ttk.Label(key_frame, text="API 키 미설정", foreground="red")
        self.key_status_label.pack(side=tk.LEFT)
        
        # 카카오 인증
        auth_frame = ttk.Frame(main_frame)
        auth_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(auth_frame, text="카카오톡 인증", command=self.authenticate_kakao).pack(side=tk.LEFT, padx=(0, 10))
        self.auth_status_label = ttk.Label(auth_frame, text="인증 필요", foreground="red")
        self.auth_status_label.pack(side=tk.LEFT)
        
        # 뉴스 설정
        news_frame = ttk.LabelFrame(main_frame, text="뉴스 설정", padding="10")
        news_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(news_frame, text="개수:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.count_var = tk.StringVar(value="5")
        ttk.Spinbox(news_frame, from_=1, to=5, textvariable=self.count_var, width=5).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(news_frame, text="정렬:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.sort_var = tk.StringVar(value="최신")
        sort_combo = ttk.Combobox(news_frame, textvariable=self.sort_var, values=["최신", "관련도"], state="readonly", width=10)
        sort_combo.grid(row=0, column=3)
        sort_combo.bind("<<ComboboxSelected>>", self.on_sort_change)
        
        # 키워드 프레임 (관련도순 선택 시에만 표시)
        self.keyword_frame = ttk.Frame(news_frame)
        self.keyword_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(self.keyword_frame, text="키워드:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.keyword_var = tk.StringVar(value="정치, 경제, 사회")
        self.keyword_entry = ttk.Entry(self.keyword_frame, textvariable=self.keyword_var, width=30)
        self.keyword_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 키워드 예시
        keyword_example = ttk.Label(self.keyword_frame, text="예시: 정치, 경제, 사회, 스포츠, 연예, IT, 부동산, 주식", 
                                   font=("Arial", 8), foreground="gray")
        keyword_example.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 스케줄 설정
        schedule_frame = ttk.LabelFrame(main_frame, text="스케줄 설정", padding="10")
        schedule_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 간격 모드
        self.mode_var = tk.StringVar(value="interval")
        ttk.Radiobutton(schedule_frame, text="간격 모드", variable=self.mode_var, value="interval", command=self.on_mode_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(schedule_frame, text="알람 모드", variable=self.mode_var, value="alarm", command=self.on_mode_change).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 간격 설정
        self.interval_label = ttk.Label(schedule_frame, text="간격(분):")
        self.interval_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.interval_var = tk.StringVar(value="60")
        self.interval_spinbox = ttk.Spinbox(schedule_frame, from_=1, to=1440, textvariable=self.interval_var, width=5)
        self.interval_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(10, 0))
        
        # 알람 설정
        self.alarm_label = ttk.Label(schedule_frame, text="시간(예: 08:30,12:00,18:00):")
        self.alarm_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.alarm_var = tk.StringVar(value="08:30,12:00,18:00")
        self.alarm_entry = ttk.Entry(schedule_frame, textvariable=self.alarm_var, width=30)
        self.alarm_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=(10, 0))
        
        # 알람 모드 설명
        self.alarm_info = ttk.Label(schedule_frame, text="※ 알람 모드: 지정된 시간에만 실행 (예: 08:30, 12:00, 18:00)", 
                                   font=("Arial", 8), foreground="gray")
        self.alarm_info.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 제어 버튼
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="시작", command=self.start_scheduler)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="중지", command=self.stop_scheduler, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="실시간 전송", command=self.test_news_send).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="테스트 전송", command=self.test_send).pack(side=tk.LEFT)
        
        # 로그
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def load_keys(self):
        """../config/keys.txt에서 API 키 로드"""
        try:
            if os.path.exists("../config/keys.txt"):
                with open("../config/keys.txt", 'r', encoding='utf-8') as f:
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
    
    def load_kakao_token(self):
        """카카오톡 토큰 로드"""
        try:
            if os.path.exists("../config/kakao_token.txt"):
                with open("../config/kakao_token.txt", 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('ACCESS_TOKEN='):
                            self.access_token = line.split('=', 1)[1].strip()
                        elif line.startswith('REFRESH_TOKEN='):
                            self.refresh_token = line.split('=', 1)[1].strip()
                
                if self.access_token:
                    self.auth_status_label.config(text="인증 완료", foreground="green")
                    self.log_message("카카오톡 토큰 로드됨")
                else:
                    self.auth_status_label.config(text="인증 필요", foreground="red")
            else:
                self.auth_status_label.config(text="인증 필요", foreground="red")
        except Exception as e:
            self.log_message(f"토큰 로드 오류: {str(e)}")
            self.auth_status_label.config(text="인증 필요", foreground="red")
    
    def clean_html_entities(self, text):
        """HTML 엔티티를 일반 문자로 변환"""
        try:
            # HTML 엔티티 디코딩
            text = html.unescape(text)
            # 추가적인 정리
            text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            return text
        except Exception:
            return text
    
    def on_sort_change(self, event=None):
        """정렬 방식 변경 시 키워드 입력 칸 표시/숨김"""
        if self.sort_var.get() == "관련도":
            # 키워드 입력 칸 표시
            self.keyword_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        else:
            # 키워드 입력 칸 숨김
            self.keyword_frame.grid_remove()
    
    def on_mode_change(self):
        """스케줄 모드 변경 시 UI 업데이트"""
        if self.mode_var.get() == "interval":
            # 간격 모드: 간격 설정만 표시, 알람 설정 숨김
            self.interval_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
            self.interval_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(10, 0))
            self.alarm_label.grid_remove()
            self.alarm_entry.grid_remove()
            self.alarm_info.grid_remove()
        else:
            # 알람 모드: 알람 설정만 표시, 간격 설정 숨김
            self.interval_label.grid_remove()
            self.interval_spinbox.grid_remove()
            self.alarm_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
            self.alarm_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=(10, 0))
            self.alarm_info.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
    
    def open_key_setup(self):
        """API 키 설정 창 열기"""
        import subprocess
        import sys
        import os
        # 현재 파일의 디렉토리 (src/)를 절대 경로로 사용
        src_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([sys.executable, "key_setup.py"], cwd=src_dir)
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
            code = tk.simpledialog.askstring("인증 코드", 
                "브라우저에서 로그인 후 리다이렉트된 URL을 확인하세요.\n\n"
                "URL 예시: http://localhost:8080/callback?code=ABC123...\n"
                "이 URL에서 'code=' 뒤의 긴 문자열을 복사하여 아래에 붙여넣으세요:\n\n"
                "인증 코드:")
            
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
                    with open("../config/kakao_token.txt", 'w', encoding='utf-8') as f:
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
            
            # 검색 키워드 설정
            if self.sort_var.get() == "관련도":
                # 사용자가 입력한 키워드 사용 (쉼표로 분리된 키워드 처리)
                query = self.keyword_var.get().strip()
                if not query:
                    query = "정치, 경제, 사회"  # 기본값
                # 쉼표로 분리된 키워드를 공백으로 연결
                query = query.replace(",", " ").replace("  ", " ").strip()
            else:
                # 최신순: 시간대별 키워드
                current_hour = datetime.now().hour
                if 6 <= current_hour < 12:
                    query = "정치 경제 사회 아침뉴스"
                elif 12 <= current_hour < 18:
                    query = "경제 사회 정치 오후뉴스"
                elif 18 <= current_hour < 22:
                    query = "정치 사회 경제 저녁뉴스"
                else:
                    query = "뉴스 정치 경제 사회"
            
            # 정렬 옵션 설정
            sort_option = "date" if self.sort_var.get() == "최신" else "sim"
            
            # 충분한 개수를 가져오기 위해 더 많이 요청
            requested_count = int(self.count_var.get())
            # 전송된 뉴스가 많을 수 있으므로 더 많이 가져오기
            fetch_count = max(requested_count * 20, 100)  # 최소 100개, 요청 개수의 20배
            
            params = {
                "query": query,
                "display": min(fetch_count, 100),  # API 최대 100개 제한
                "sort": sort_option
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                news_list = []
                
                for item in data.get("items", []):
                    # HTML 태그 제거 및 엔티티 처리
                    title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                    title = self.clean_html_entities(title)
                    
                    description = item.get("description", "").replace("<b>", "").replace("</b>", "")
                    description = self.clean_html_entities(description)
                    
                    link = item.get("link", "")
                    pub_date = item.get("pubDate", "")
                    
                    news_list.append({
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": pub_date
                    })
                
                # 중복 제거 (같은 뉴스)
                news_list = self.remove_duplicates(news_list)
                
                # 전송된 뉴스 제거 (이전에 보낸 뉴스)
                requested_count = int(self.count_var.get())
                news_list = self.remove_sent_news(news_list, requested_count)
                
                # 요청한 개수만큼만 반환
                return news_list[:requested_count]
            else:
                self.log_message(f"뉴스 API 오류: {response.status_code}")
                if response.status_code == 401:
                    self.log_message("API 키가 올바르지 않습니다.")
                elif response.status_code == 403:
                    self.log_message("API 사용량이 초과되었습니다.")
                return []
                
        except Exception as e:
            self.log_message(f"뉴스 가져오기 오류: {str(e)}")
            return []
    
    def remove_duplicates(self, news_list):
        """중복 뉴스 제거"""
        try:
            seen_titles = set()
            seen_links = set()
            unique_news = []
            
            for news in news_list:
                title = news['title'].strip()
                link = news['link'].strip()
                
                # 제목과 링크로 중복 체크
                title_lower = title.lower()
                if title_lower not in seen_titles and link not in seen_links:
                    seen_titles.add(title_lower)
                    seen_links.add(link)
                    unique_news.append(news)
            
            # self.log_message(f"중복 제거: {len(news_list)}개 → {len(unique_news)}개")  # 사용자에게 숨김
            return unique_news
            
        except Exception as e:
            self.log_message(f"중복 제거 오류: {str(e)}")
            return news_list
    
    def remove_sent_news(self, news_list, requested_count):
        """이전에 전송된 뉴스 제거"""
        try:
            new_news = []
            removed_count = 0
            
            for news in news_list:
                link = news['link'].strip()
                title = news['title'].strip()
                
                # 전송된 뉴스인지 확인
                if link not in self.sent_urls:
                    new_news.append(news)
                else:
                    removed_count += 1
            
            if removed_count > 0:
                # self.log_message(f"전송된 뉴스 제거: {removed_count}개")  # 사용자에게 숨김
                pass
            
            # 요청한 개수만큼 반환 (부족하면 있는 만큼만)
            return new_news[:requested_count]
            
        except Exception as e:
            self.log_message(f"전송된 뉴스 제거 오류: {str(e)}")
            return news_list
    
    def filter_high_view_news(self, news_list):
        """조회수 높은 뉴스 선별"""
        try:
            # 조회수 높은 뉴스 특징을 기반으로 선별
            scored_news = []
            
            for news in news_list:
                score = 0
                title = news['title'].lower()
                description = news['description'].lower()
                
                # 조회수 높은 뉴스 키워드 (화제성, 중요도)
                hot_keywords = [
                    '대통령', '총리', '국회', '정부', '정치',
                    '경제', '금융', '주식', '부동산', '기업',
                    '사건', '사고', '범죄', '교통', '교육',
                    '코로나', '감염', '백신', '의료', '건강',
                    '날씨', '태풍', '지진', '재해', '안전',
                    '스포츠', '축구', '야구', '올림픽', '월드컵',
                    '연예', '드라마', '영화', '음악', '가수',
                    'IT', '기술', '인공지능', '로봇', '스마트폰'
                ]
                
                # 키워드 매칭 점수
                for keyword in hot_keywords:
                    if keyword in title:
                        score += 3
                    if keyword in description:
                        score += 1
                
                # 제목 길이 (적당한 길이가 조회수 높음)
                title_len = len(news['title'])
                if 20 <= title_len <= 60:
                    score += 2
                elif 10 <= title_len <= 80:
                    score += 1
                
                # 설명 길이 (충분한 설명이 있는 뉴스)
                desc_len = len(news['description'])
                if desc_len > 50:
                    score += 1
                
                # 발행 시간 (최근 뉴스 우선)
                if news['pub_date']:
                    score += 1
                
                scored_news.append((news, score))
            
            # 점수 순으로 정렬
            scored_news.sort(key=lambda x: x[1], reverse=True)
            
            # 상위 뉴스만 반환
            return [news for news, score in scored_news]
            
        except Exception as e:
            self.log_message(f"조회수 뉴스 선별 오류: {str(e)}")
            return news_list
    
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
            message = "📰 오늘의 최신 뉴스\n\n"
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
                # 간격 모드 (분 단위)
                interval = int(self.interval_var.get())
                schedule.every(interval).minutes.do(self.send_news_job)
                self.log_message(f"간격 모드 시작: {interval}분마다")
                
                # 즉시 첫 뉴스 전송
                self.log_message("첫 뉴스 전송 중...")
                self.send_news_job()
                
            else:
                # 알람 모드
                times = [t.strip() for t in self.alarm_var.get().split(",")]
                for time_str in times:
                    hour, minute = map(int, time_str.split(":"))
                    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.send_news_job)
                self.log_message(f"알람 모드 시작: {', '.join(times)}")
                
                # 알람모드 자동 중지 스케줄 추가 (마지막 시간 + 1분 후)
                if times:
                    last_time = max(times, key=lambda x: (int(x.split(':')[0]), int(x.split(':')[1])))
                    last_hour, last_minute = map(int, last_time.split(":"))
                    # 마지막 시간 + 1분 후에 자동 중지
                    if last_minute == 59:
                        auto_stop_hour = (last_hour + 1) % 24
                        auto_stop_minute = 0
                    else:
                        auto_stop_hour = last_hour
                        auto_stop_minute = last_minute + 1
                    
                    schedule.every().day.at(f"{auto_stop_hour:02d}:{auto_stop_minute:02d}").do(self.auto_stop_alarm)
            
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
    
    def auto_stop_alarm(self):
        """알람모드 자동 중지"""
        if self.mode_var.get() == "alarm":
            self.log_message("알람모드 자동 중지: 모든 시간 완료")
            self.stop_scheduler()
    
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
    
    def test_news_send(self):
        """뉴스 수집 및 카카오톡 전송 테스트"""
        if not self.naver_id or not self.naver_secret:
            messagebox.showwarning("경고", "먼저 API 키를 설정해주세요.")
            return
        
        if not self.access_token:
            messagebox.showwarning("경고", "먼저 카카오톡 인증을 완료해주세요.")
            return
        
        try:
            self.log_message("🔥 뉴스 수집 및 전송 테스트 시작...")
            
            # 뉴스 가져오기
            news_list = self.get_news()
            
            if not news_list:
                self.log_message("❌ 뉴스를 가져올 수 없습니다.")
                messagebox.showwarning("경고", "뉴스를 가져올 수 없습니다. API 키를 확인해주세요.")
                return
            
            self.log_message(f"✅ {len(news_list)}개의 뉴스를 가져왔습니다.")
            
            # 메시지 구성
            message = "📰 오늘의 최신 뉴스\n\n"
            for i, news in enumerate(news_list[:5], 1):
                message += f"{i}. {news['title']}\n"
                if news['link']:
                    message += f"   링크: {news['link']}\n"
                message += "\n"
            
            # 카카오톡으로 전송
            self.log_message("📱 카카오톡으로 전송 중...")
            if self.send_to_kakao(message):
                self.log_message("✅ 뉴스 전송 성공!")
                messagebox.showinfo("성공", "뉴스가 카카오톡으로 전송되었습니다!\n폰에서 알림을 확인해주세요.")
            else:
                self.log_message("❌ 뉴스 전송 실패")
                messagebox.showerror("실패", "뉴스 전송에 실패했습니다.")
                
        except Exception as e:
            self.log_message(f"❌ 뉴스 전송 테스트 오류: {str(e)}")
            messagebox.showerror("오류", f"뉴스 전송 테스트 중 오류가 발생했습니다: {str(e)}")
    
    def run(self):
        """앱 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = NewsAutomation()
    app.run()
