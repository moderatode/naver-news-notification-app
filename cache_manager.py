#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
중복 기사 방지 캐시 관리 모듈
- 전송된 뉴스 URL을 로컬에 저장
- 중복 전송 방지
- 캐시 정리 및 관리
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Set, List, Dict
import hashlib

class CacheManager:
    def __init__(self, cache_file: str = "news_cache.json"):
        self.cache_file = cache_file
        self.cache_data = {
            "sent_urls": set(),  # 전송된 URL들
            "sent_titles": set(),  # 전송된 제목들 (제목 기반 중복 방지)
            "last_cleanup": None,  # 마지막 정리 시간
            "max_cache_size": 1000,  # 최대 캐시 크기
            "cache_expire_days": 7  # 캐시 만료 일수
        }
        self._load_cache()
    
    def _load_cache(self):
        """캐시 데이터 로드"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache_data["sent_urls"] = set(data.get("sent_urls", []))
                    self.cache_data["sent_titles"] = set(data.get("sent_titles", []))
                    self.cache_data["last_cleanup"] = data.get("last_cleanup")
                    self.cache_data["max_cache_size"] = data.get("max_cache_size", 1000)
                    self.cache_data["cache_expire_days"] = data.get("cache_expire_days", 7)
        except Exception as e:
            print(f"캐시 로드 오류: {str(e)}")
            self._save_cache()
    
    def _save_cache(self):
        """캐시 데이터 저장"""
        try:
            data = {
                "sent_urls": list(self.cache_data["sent_urls"]),
                "sent_titles": list(self.cache_data["sent_titles"]),
                "last_cleanup": self.cache_data["last_cleanup"],
                "max_cache_size": self.cache_data["max_cache_size"],
                "cache_expire_days": self.cache_data["cache_expire_days"]
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"캐시 저장 오류: {str(e)}")
    
    def is_sent(self, url: str, title: str = None) -> bool:
        """
        뉴스가 이미 전송되었는지 확인
        
        Args:
            url: 뉴스 URL
            title: 뉴스 제목 (선택사항)
        
        Returns:
            이미 전송된 뉴스인지 여부
        """
        try:
            # URL 기반 중복 체크
            if url in self.cache_data["sent_urls"]:
                return True
            
            # 제목 기반 중복 체크 (URL이 없는 경우)
            if title:
                title_hash = self._hash_title(title)
                if title_hash in self.cache_data["sent_titles"]:
                    return True
            
            return False
            
        except Exception as e:
            print(f"중복 체크 오류: {str(e)}")
            return False
    
    def mark_sent(self, url: str, title: str = None):
        """
        뉴스를 전송됨으로 표시
        
        Args:
            url: 뉴스 URL
            title: 뉴스 제목 (선택사항)
        """
        try:
            # URL 저장
            if url:
                self.cache_data["sent_urls"].add(url)
            
            # 제목 해시 저장
            if title:
                title_hash = self._hash_title(title)
                self.cache_data["sent_titles"].add(title_hash)
            
            # 캐시 크기 체크
            self._check_cache_size()
            
            # 주기적 정리
            self._cleanup_if_needed()
            
            # 캐시 저장
            self._save_cache()
            
        except Exception as e:
            print(f"전송 표시 오류: {str(e)}")
    
    def _hash_title(self, title: str) -> str:
        """제목 해시 생성"""
        try:
            # 제목 정규화 (공백 제거, 소문자 변환)
            normalized_title = title.strip().lower()
            # 해시 생성
            return hashlib.md5(normalized_title.encode('utf-8')).hexdigest()
        except Exception as e:
            print(f"제목 해시 생성 오류: {str(e)}")
            return title
    
    def _check_cache_size(self):
        """캐시 크기 체크 및 정리"""
        try:
            max_size = self.cache_data["max_cache_size"]
            current_size = len(self.cache_data["sent_urls"]) + len(self.cache_data["sent_titles"])
            
            if current_size > max_size:
                # 오래된 항목들 제거 (FIFO 방식)
                self._cleanup_old_entries()
                
        except Exception as e:
            print(f"캐시 크기 체크 오류: {str(e)}")
    
    def _cleanup_if_needed(self):
        """필요시 캐시 정리"""
        try:
            last_cleanup = self.cache_data["last_cleanup"]
            if not last_cleanup:
                self.cache_data["last_cleanup"] = datetime.now().isoformat()
                return
            
            # 마지막 정리로부터 24시간이 지났으면 정리
            last_cleanup_time = datetime.fromisoformat(last_cleanup)
            if datetime.now() - last_cleanup_time > timedelta(hours=24):
                self._cleanup_old_entries()
                self.cache_data["last_cleanup"] = datetime.now().isoformat()
                
        except Exception as e:
            print(f"캐시 정리 체크 오류: {str(e)}")
    
    def _cleanup_old_entries(self):
        """오래된 캐시 항목 정리"""
        try:
            # 현재 크기의 50%만 유지
            target_size = self.cache_data["max_cache_size"] // 2
            
            # URL 캐시 정리
            if len(self.cache_data["sent_urls"]) > target_size:
                urls_list = list(self.cache_data["sent_urls"])
                self.cache_data["sent_urls"] = set(urls_list[-target_size:])
            
            # 제목 캐시 정리
            if len(self.cache_data["sent_titles"]) > target_size:
                titles_list = list(self.cache_data["sent_titles"])
                self.cache_data["sent_titles"] = set(titles_list[-target_size:])
            
            print(f"캐시 정리 완료: {len(self.cache_data['sent_urls'])} URLs, {len(self.cache_data['sent_titles'])} titles")
            
        except Exception as e:
            print(f"캐시 정리 오류: {str(e)}")
    
    def get_cache_stats(self) -> Dict:
        """캐시 통계 정보"""
        try:
            return {
                "sent_urls_count": len(self.cache_data["sent_urls"]),
                "sent_titles_count": len(self.cache_data["sent_titles"]),
                "last_cleanup": self.cache_data["last_cleanup"],
                "max_cache_size": self.cache_data["max_cache_size"],
                "cache_expire_days": self.cache_data["cache_expire_days"]
            }
        except Exception as e:
            print(f"캐시 통계 오류: {str(e)}")
            return {}
    
    def clear_cache(self):
        """캐시 전체 삭제"""
        try:
            self.cache_data["sent_urls"].clear()
            self.cache_data["sent_titles"].clear()
            self.cache_data["last_cleanup"] = None
            self._save_cache()
            print("캐시가 삭제되었습니다.")
        except Exception as e:
            print(f"캐시 삭제 오류: {str(e)}")
    
    def set_cache_settings(self, max_size: int = 1000, expire_days: int = 7):
        """캐시 설정 변경"""
        try:
            self.cache_data["max_cache_size"] = max_size
            self.cache_data["cache_expire_days"] = expire_days
            self._save_cache()
            print(f"캐시 설정이 변경되었습니다: 최대 {max_size}개, 만료 {expire_days}일")
        except Exception as e:
            print(f"캐시 설정 변경 오류: {str(e)}")
    
    def export_cache(self, export_file: str = "news_cache_export.json"):
        """캐시 데이터 내보내기"""
        try:
            export_data = {
                "export_time": datetime.now().isoformat(),
                "sent_urls": list(self.cache_data["sent_urls"]),
                "sent_titles": list(self.cache_data["sent_titles"]),
                "stats": self.get_cache_stats()
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"캐시 데이터가 {export_file}로 내보내졌습니다.")
            return True
            
        except Exception as e:
            print(f"캐시 내보내기 오류: {str(e)}")
            return False
    
    def import_cache(self, import_file: str):
        """캐시 데이터 가져오기"""
        try:
            if not os.path.exists(import_file):
                print(f"파일을 찾을 수 없습니다: {import_file}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 기존 캐시와 병합
            self.cache_data["sent_urls"].update(import_data.get("sent_urls", []))
            self.cache_data["sent_titles"].update(import_data.get("sent_titles", []))
            
            self._save_cache()
            print(f"캐시 데이터가 {import_file}에서 가져와졌습니다.")
            return True
            
        except Exception as e:
            print(f"캐시 가져오기 오류: {str(e)}")
            return False
    
    def filter_new_news(self, news_list: List[Dict]) -> List[Dict]:
        """
        뉴스 리스트에서 새로운 뉴스만 필터링
        
        Args:
            news_list: 뉴스 리스트
        
        Returns:
            새로운 뉴스만 포함된 리스트
        """
        try:
            new_news = []
            for news in news_list:
                url = news.get('link', '')
                title = news.get('title', '')
                
                if not self.is_sent(url, title):
                    new_news.append(news)
            
            return new_news
            
        except Exception as e:
            print(f"뉴스 필터링 오류: {str(e)}")
            return news_list
