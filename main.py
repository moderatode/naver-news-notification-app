#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 뉴스 자동화 앱
- 네이버 뉴스 API를 통해 핫한 뉴스를 가져와 카카오톡 나에게 보내기로 전송
- GUI를 통한 스케줄 설정 (간격 모드 / 알람 모드)
- OAuth 토큰 자동 관리 및 중복 기사 방지
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import time
from datetime import datetime, timedelta
import schedule
import pytz
from news_api import NaverNewsAPI
from kakao_api import KakaoAPI
from config_manager import ConfigManager
from cache_manager import CacheManager

class NewsAutomationApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("네이버 뉴스 자동화")
        self.root.geometry("600x700")
        
        # API 인스턴스들
        self.news_api = NaverNewsAPI()
        self.kakao_api = KakaoAPI()
        self.config_manager = ConfigManager()
        self.cache_manager = CacheManager()
        
        # 스케줄링 관련
        self.scheduler_thread = None
        self.is_running = False
        
        # 설정 로드
        self.config = self.config_manager.load_config()
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """GUI 인터페이스 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="네이버 뉴스 자동화", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 카카오 인증 섹션
        auth_frame = ttk.LabelFrame(main_frame, text="카카오톡 인증", padding="10")
        auth_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.auth_status_label = ttk.Label(auth_frame, text="인증 필요", foreground="red")
        self.auth_status_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(auth_frame, text="카카오톡 인증", command=self.authenticate_kakao).grid(row=0, column=1, padx=(10, 0))
        
        # 뉴스 설정 섹션
        news_frame = ttk.LabelFrame(main_frame, text="뉴스 설정", padding="10")
        news_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(news_frame, text="표시 개수:").grid(row=0, column=0, sticky=tk.W)
        self.count_var = tk.StringVar(value="5")
        count_spinbox = ttk.Spinbox(news_frame, from_=1, to=20, textvariable=self.count_var, width=5)
        count_spinbox.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(news_frame, text="정렬:").grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
        self.sort_var = tk.StringVar(value="최신")
        sort_combo = ttk.Combobox(news_frame, textvariable=self.sort_var, values=["최신", "관련도"], state="readonly", width=10)
        sort_combo.grid(row=0, column=3, padx=(5, 0))
        
        # 스케줄 설정 섹션
        schedule_frame = ttk.LabelFrame(main_frame, text="스케줄 설정", padding="10")
        schedule_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 스케줄 모드 선택
        self.schedule_mode = tk.StringVar(value="interval")
        ttk.Radiobutton(schedule_frame, text="간격 모드", variable=self.schedule_mode, value="interval", command=self.on_mode_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(schedule_frame, text="알람 모드", variable=self.schedule_mode, value="alarm", command=self.on_mode_change).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 간격 모드 설정
        self.interval_frame = ttk.Frame(schedule_frame)
        self.interval_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(self.interval_frame, text="간격:").grid(row=0, column=0, sticky=tk.W)
        self.interval_var = tk.StringVar(value="1")
        interval_spinbox = ttk.Spinbox(self.interval_frame, from_=1, to=24, textvariable=self.interval_var, width=5)
        interval_spinbox.grid(row=0, column=1, padx=(5, 0))
        ttk.Label(self.interval_frame, text="시간").grid(row=0, column=2, padx=(5, 0))
        
        # 알람 모드 설정
        self.alarm_frame = ttk.Frame(schedule_frame)
        self.alarm_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(self.alarm_frame, text="시간:").grid(row=0, column=0, sticky=tk.W)
        self.alarm_times_var = tk.StringVar(value="08:30,12:00,18:00")
        alarm_entry = ttk.Entry(self.alarm_frame, textvariable=self.alarm_times_var, width=30)
        alarm_entry.grid(row=0, column=1, padx=(5, 0))
        ttk.Label(self.alarm_frame, text="(예: 08:30,12:00,18:00)").grid(row=0, column=2, padx=(5, 0))
        
        # 요일 선택
        ttk.Label(self.alarm_frame, text="요일:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.weekdays_frame = ttk.Frame(self.alarm_frame)
        self.weekdays_frame.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        self.weekday_vars = {}
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for i, day in enumerate(weekdays):
            var = tk.BooleanVar(value=True if i < 5 else False)  # 평일 기본 선택
            self.weekday_vars[day] = var
            ttk.Checkbutton(self.weekdays_frame, text=day, variable=var).grid(row=0, column=i, padx=2)
        
        # 제어 버튼
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        self.start_button = ttk.Button(control_frame, text="시작", command=self.start_scheduler)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="중지", command=self.stop_scheduler, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(control_frame, text="설정 저장", command=self.save_settings).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(control_frame, text="테스트 전송", command=self.test_send).grid(row=0, column=3)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.on_mode_change()  # 초기 모드 설정
        
    def on_mode_change(self):
        """스케줄 모드 변경 시 UI 업데이트"""
        if self.schedule_mode.get() == "interval":
            self.interval_frame.grid()
            self.alarm_frame.grid_remove()
        else:
            self.interval_frame.grid_remove()
            self.alarm_frame.grid()
    
    def log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def authenticate_kakao(self):
        """카카오톡 OAuth 인증"""
        try:
            self.log_message("카카오톡 인증을 시작합니다...")
            success = self.kakao_api.authenticate()
            if success:
                self.auth_status_label.config(text="인증 완료", foreground="green")
                self.log_message("카카오톡 인증이 완료되었습니다.")
            else:
                self.auth_status_label.config(text="인증 실패", foreground="red")
                self.log_message("카카오톡 인증에 실패했습니다.")
        except Exception as e:
            self.log_message(f"인증 오류: {str(e)}")
            messagebox.showerror("오류", f"인증 중 오류가 발생했습니다: {str(e)}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if not self.kakao_api.is_authenticated():
            messagebox.showwarning("경고", "먼저 카카오톡 인증을 완료해주세요.")
            return
        
        try:
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # 기존 스케줄 클리어
            schedule.clear()
            
            if self.schedule_mode.get() == "interval":
                # 간격 모드
                interval = int(self.interval_var.get())
                schedule.every(interval).hours.do(self.send_news_job)
                self.log_message(f"간격 모드로 설정: {interval}시간마다 실행")
            else:
                # 알람 모드
                times = [t.strip() for t in self.alarm_times_var.get().split(",")]
                weekdays = [day for day, var in self.weekday_vars.items() if var.get()]
                
                for time_str in times:
                    hour, minute = map(int, time_str.split(":"))
                    for day in weekdays:
                        day_map = {"월": "monday", "화": "tuesday", "수": "wednesday", 
                                 "목": "thursday", "금": "friday", "토": "saturday", "일": "sunday"}
                        getattr(schedule.every(), day_map[day]).at(f"{hour:02d}:{minute:02d}").do(self.send_news_job)
                
                self.log_message(f"알람 모드로 설정: {', '.join(times)} ({', '.join(weekdays)})")
            
            # 스케줄러 스레드 시작
            self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            self.log_message("스케줄러가 시작되었습니다.")
            
        except Exception as e:
            self.log_message(f"스케줄러 시작 오류: {str(e)}")
            messagebox.showerror("오류", f"스케줄러 시작 중 오류가 발생했습니다: {str(e)}")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.is_running = False
        schedule.clear()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log_message("스케줄러가 중지되었습니다.")
    
    def run_scheduler(self):
        """스케줄러 실행 루프"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def send_news_job(self):
        """뉴스 전송 작업"""
        try:
            self.log_message("뉴스 전송 작업을 시작합니다...")
            
            # 뉴스 가져오기
            count = int(self.count_var.get())
            sort = "date" if self.sort_var.get() == "최신" else "sim"
            
            news_list = self.news_api.get_hot_news(count=count, sort=sort)
            
            if not news_list:
                self.log_message("가져올 뉴스가 없습니다.")
                return
            
            # 중복 제거
            new_news = []
            for news in news_list:
                if not self.cache_manager.is_sent(news['link']):
                    new_news.append(news)
            
            if not new_news:
                self.log_message("새로운 뉴스가 없습니다.")
                return
            
            # 카카오톡으로 전송
            success_count = 0
            for news in new_news:
                try:
                    message = f"🔥 {news['title']}\n\n{news['description']}\n\n링크: {news['link']}"
                    if self.kakao_api.send_message(message):
                        self.cache_manager.mark_sent(news['link'])
                        success_count += 1
                        self.log_message(f"뉴스 전송 완료: {news['title'][:30]}...")
                    else:
                        self.log_message(f"뉴스 전송 실패: {news['title'][:30]}...")
                except Exception as e:
                    self.log_message(f"뉴스 전송 오류: {str(e)}")
            
            self.log_message(f"뉴스 전송 완료: {success_count}/{len(new_news)}개")
            
        except Exception as e:
            self.log_message(f"뉴스 전송 작업 오류: {str(e)}")
    
    def test_send(self):
        """테스트 전송"""
        if not self.kakao_api.is_authenticated():
            messagebox.showwarning("경고", "먼저 카카오톡 인증을 완료해주세요.")
            return
        
        try:
            self.log_message("테스트 전송을 시작합니다...")
            message = "🧪 테스트 메시지입니다.\n\n네이버 뉴스 자동화 앱이 정상적으로 작동합니다."
            if self.kakao_api.send_message(message):
                self.log_message("테스트 전송이 완료되었습니다.")
                messagebox.showinfo("성공", "테스트 메시지가 전송되었습니다.")
            else:
                self.log_message("테스트 전송에 실패했습니다.")
                messagebox.showerror("실패", "테스트 전송에 실패했습니다.")
        except Exception as e:
            self.log_message(f"테스트 전송 오류: {str(e)}")
            messagebox.showerror("오류", f"테스트 전송 중 오류가 발생했습니다: {str(e)}")
    
    def save_settings(self):
        """설정 저장"""
        try:
            settings = {
                "count": int(self.count_var.get()),
                "sort": self.sort_var.get(),
                "schedule_mode": self.schedule_mode.get(),
                "interval": int(self.interval_var.get()),
                "alarm_times": self.alarm_times_var.get(),
                "weekdays": {day: var.get() for day, var in self.weekday_vars.items()}
            }
            
            self.config_manager.save_config(settings)
            self.log_message("설정이 저장되었습니다.")
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
        except Exception as e:
            self.log_message(f"설정 저장 오류: {str(e)}")
            messagebox.showerror("오류", f"설정 저장 중 오류가 발생했습니다: {str(e)}")
    
    def load_settings(self):
        """설정 로드"""
        try:
            if self.config:
                self.count_var.set(self.config.get("count", 5))
                self.sort_var.set(self.config.get("sort", "최신"))
                self.schedule_mode.set(self.config.get("schedule_mode", "interval"))
                self.interval_var.set(self.config.get("interval", 1))
                self.alarm_times_var.set(self.config.get("alarm_times", "08:30,12:00,18:00"))
                
                weekdays = self.config.get("weekdays", {})
                for day, var in self.weekday_vars.items():
                    var.set(weekdays.get(day, True if day in ["월", "화", "수", "목", "금"] else False))
                
                self.on_mode_change()
                self.log_message("설정이 로드되었습니다.")
        except Exception as e:
            self.log_message(f"설정 로드 오류: {str(e)}")
    
    def run(self):
        """앱 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = NewsAutomationApp()
    app.run()
