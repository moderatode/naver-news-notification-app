#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 키 설정 GUI
- 네이버, 카카오 API 키를 입력하여 keys.txt에 저장
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

class KeySetupGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("API 키 설정")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 화면 중앙에 배치
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
        # 키 파일 경로
        self.keys_file = "keys.txt"
        
        self.setup_ui()
        self.load_existing_keys()
        
    def setup_ui(self):
        """GUI 인터페이스 설정"""
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
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바와 캔버스 배치
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 마우스 휠 바인딩
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 제목
        title_label = ttk.Label(main_frame, text="API 키 설정", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 네이버 API 키 섹션
        naver_frame = ttk.LabelFrame(main_frame, text="네이버 뉴스 API", padding="15")
        naver_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(naver_frame, text="Client ID:").pack(anchor=tk.W)
        self.naver_id_var = tk.StringVar()
        naver_id_entry = ttk.Entry(naver_frame, textvariable=self.naver_id_var, width=50)
        naver_id_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(naver_frame, text="Client Secret:").pack(anchor=tk.W)
        self.naver_secret_var = tk.StringVar()
        naver_secret_entry = ttk.Entry(naver_frame, textvariable=self.naver_secret_var, width=50, show="*")
        naver_secret_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 카카오 API 키 섹션
        kakao_frame = ttk.LabelFrame(main_frame, text="카카오톡 API", padding="15")
        kakao_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(kakao_frame, text="REST API Key:").pack(anchor=tk.W)
        self.kakao_key_var = tk.StringVar()
        kakao_key_entry = ttk.Entry(kakao_frame, textvariable=self.kakao_key_var, width=50)
        kakao_key_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 안내 메시지
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        info_text = """API 키 발급 방법:
• 네이버: https://developers.naver.com → 애플리케이션 등록 → 검색 API
• 카카오: https://developers.kakao.com → 내 애플리케이션 → 앱 키"""
        
        info_label = ttk.Label(info_frame, text=info_text, font=("Arial", 9), foreground="gray")
        info_label.pack(anchor=tk.W)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="저장", command=self.save_keys).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="불러오기", command=self.load_existing_keys).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="닫기", command=self.root.destroy).pack(side=tk.RIGHT)
        
    def load_existing_keys(self):
        """기존 키 파일에서 키 불러오기"""
        try:
            if os.path.exists(self.keys_file):
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    if line.startswith('NAVER_ID='):
                        self.naver_id_var.set(line.split('=', 1)[1].strip())
                    elif line.startswith('NAVER_SECRET='):
                        self.naver_secret_var.set(line.split('=', 1)[1].strip())
                    elif line.startswith('KAKAO_KEY='):
                        self.kakao_key_var.set(line.split('=', 1)[1].strip())
        except Exception as e:
            print(f"키 파일 로드 오류: {str(e)}")
    
    def save_keys(self):
        """키를 파일에 저장"""
        try:
            # 입력 검증
            if not self.naver_id_var.get().strip():
                messagebox.showwarning("경고", "네이버 Client ID를 입력해주세요.")
                return
            
            if not self.naver_secret_var.get().strip():
                messagebox.showwarning("경고", "네이버 Client Secret을 입력해주세요.")
                return
                
            if not self.kakao_key_var.get().strip():
                messagebox.showwarning("경고", "카카오 REST API Key를 입력해주세요.")
                return
            
            # 키 파일에 저장
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                f.write(f"NAVER_ID={self.naver_id_var.get().strip()}\n")
                f.write(f"NAVER_SECRET={self.naver_secret_var.get().strip()}\n")
                f.write(f"KAKAO_KEY={self.kakao_key_var.get().strip()}\n")
            
            messagebox.showinfo("성공", "API 키가 저장되었습니다!")
            
        except Exception as e:
            messagebox.showerror("오류", f"키 저장 중 오류가 발생했습니다: {str(e)}")
    
    def run(self):
        """GUI 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = KeySetupGUI()
    app.run()
