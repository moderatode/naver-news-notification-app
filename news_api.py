#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 뉴스 API 연동 모듈
- 네이버 뉴스 검색 API를 사용하여 핫한 뉴스 가져오기
- 공식 API 우선 사용, 필요시 크롤링 대안 제공
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class NaverNewsAPI:
    def __init__(self):
        # 네이버 뉴스 검색 API 설정
        from api_keys import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
        self.client_id = NAVER_CLIENT_ID
        self.client_secret = NAVER_CLIENT_SECRET
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # API 사용량 제한을 위한 설정
        self.last_request_time = 0
        self.min_request_interval = 1  # 최소 1초 간격
        
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """API 요청 실행 (속도 제한 적용)"""
        # API 사용량 제한 체크
        current_time = time.time()
        if current_time - self.last_request_time < self.min_request_interval:
            time.sleep(self.min_request_interval - (current_time - self.last_request_time))
        
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API 요청 실패: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {str(e)}")
            return None
    
    def get_hot_news(self, count: int = 5, sort: str = "date", query: str = "") -> List[Dict]:
        """
        핫한 뉴스 가져오기
        
        Args:
            count: 가져올 뉴스 개수 (최대 100)
            sort: 정렬 방식 ("date": 최신순, "sim": 관련도순)
            query: 검색 쿼리 (빈 문자열이면 전체 뉴스)
        
        Returns:
            뉴스 리스트
        """
        try:
            # 검색 쿼리 설정 (빈 문자열이면 인기 키워드로 검색)
            if not query:
                # 현재 시간대별 인기 키워드
                current_hour = datetime.now().hour
                if 6 <= current_hour < 12:
                    query = "아침뉴스 정치 경제"
                elif 12 <= current_hour < 18:
                    query = "오후뉴스 사회 경제"
                elif 18 <= current_hour < 22:
                    query = "저녁뉴스 정치 사회"
                else:
                    query = "뉴스 정치 경제 사회"
            
            params = {
                "query": query,
                "display": min(count, 100),  # 최대 100개
                "sort": sort,
                "start": 1
            }
            
            # API 요청
            result = self._make_request(params)
            
            if not result or "items" not in result:
                print("뉴스 데이터를 가져올 수 없습니다.")
                return []
            
            # 뉴스 데이터 정제
            news_list = []
            for item in result["items"]:
                try:
                    # HTML 태그 제거
                    title = self._clean_html(item.get("title", ""))
                    description = self._clean_html(item.get("description", ""))
                    
                    # 링크 정리
                    link = item.get("link", "")
                    if link and "naver.com" in link:
                        # 네이버 뉴스 링크인 경우 직접 링크로 변환
                        link = self._convert_naver_link(link)
                    
                    news_item = {
                        "title": title,
                        "description": description,
                        "link": link,
                        "pub_date": item.get("pubDate", ""),
                        "source": item.get("originallink", ""),
                        "category": self._categorize_news(title, description)
                    }
                    
                    # 필수 필드 검증
                    if news_item["title"] and news_item["link"]:
                        news_list.append(news_item)
                        
                except Exception as e:
                    print(f"뉴스 아이템 처리 오류: {str(e)}")
                    continue
            
            print(f"총 {len(news_list)}개의 뉴스를 가져왔습니다.")
            return news_list
            
        except Exception as e:
            print(f"뉴스 가져오기 오류: {str(e)}")
            return []
    
    def get_news_by_category(self, category: str, count: int = 5) -> List[Dict]:
        """
        카테고리별 뉴스 가져오기
        
        Args:
            category: 뉴스 카테고리 ("정치", "경제", "사회", "생활", "세계", "IT")
            count: 가져올 뉴스 개수
        
        Returns:
            뉴스 리스트
        """
        category_queries = {
            "정치": "정치 국회 정부",
            "경제": "경제 금융 주식",
            "사회": "사회 사건 사고",
            "생활": "생활 건강 문화",
            "세계": "국제 해외",
            "IT": "IT 기술 과학"
        }
        
        query = category_queries.get(category, category)
        return self.get_hot_news(count=count, query=query)
    
    def get_trending_keywords(self) -> List[str]:
        """
        현재 트렌딩 키워드 가져오기
        
        Returns:
            트렌딩 키워드 리스트
        """
        try:
            # 현재 시간대별 인기 키워드
            current_hour = datetime.now().hour
            if 6 <= current_hour < 12:
                keywords = ["정치", "경제", "사회", "아침뉴스"]
            elif 12 <= current_hour < 18:
                keywords = ["경제", "사회", "정치", "오후뉴스"]
            elif 18 <= current_hour < 22:
                keywords = ["정치", "사회", "경제", "저녁뉴스"]
            else:
                keywords = ["뉴스", "정치", "경제", "사회"]
            
            return keywords
            
        except Exception as e:
            print(f"트렌딩 키워드 가져오기 오류: {str(e)}")
            return ["뉴스", "정치", "경제", "사회"]
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', text)
        # HTML 엔티티 디코딩
        clean_text = clean_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        clean_text = clean_text.replace('&quot;', '"').replace('&#39;', "'")
        # 연속된 공백 제거
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
    def _convert_naver_link(self, link: str) -> str:
        """네이버 뉴스 링크를 직접 링크로 변환"""
        try:
            # 네이버 뉴스 링크인 경우 직접 링크로 변환
            if "news.naver.com" in link:
                # 이미 직접 링크인 경우 그대로 반환
                return link
            elif "naver.com" in link:
                # 네이버 뉴스 링크로 변환
                return link
            else:
                return link
        except:
            return link
    
    def _categorize_news(self, title: str, description: str) -> str:
        """뉴스 카테고리 분류"""
        text = (title + " " + description).lower()
        
        if any(keyword in text for keyword in ["정치", "국회", "정부", "대통령", "총리", "정당"]):
            return "정치"
        elif any(keyword in text for keyword in ["경제", "금융", "주식", "부동산", "기업", "은행"]):
            return "경제"
        elif any(keyword in text for keyword in ["사회", "사건", "사고", "범죄", "교통", "교육"]):
            return "사회"
        elif any(keyword in text for keyword in ["생활", "건강", "문화", "스포츠", "연예", "음식"]):
            return "생활"
        elif any(keyword in text for keyword in ["국제", "해외", "외교", "북한", "미국", "중국"]):
            return "세계"
        elif any(keyword in text for keyword in ["IT", "기술", "과학", "인공지능", "로봇", "스마트폰"]):
            return "IT"
        else:
            return "기타"
    
    def test_api_connection(self) -> bool:
        """API 연결 테스트"""
        try:
            result = self.get_hot_news(count=1)
            return len(result) > 0
        except Exception as e:
            print(f"API 연결 테스트 실패: {str(e)}")
            return False

# 크롤링 대안 클래스 (API 사용 불가시)
class NaverNewsCrawler:
    def __init__(self):
        self.base_url = "https://news.naver.com"
        
    def get_hot_news(self, count: int = 5) -> List[Dict]:
        """
        네이버 뉴스 크롤링 (API 대안)
        주의: 이 방법은 네이버의 robots.txt 및 이용약관을 확인해야 합니다.
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # 네이버 뉴스 메인 페이지 크롤링
            response = requests.get(self.base_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []
            
            # 메인 뉴스 섹션에서 뉴스 추출
            news_items = soup.find_all('div', class_='newsnow_tx_inner')
            
            for item in news_items[:count]:
                try:
                    title_elem = item.find('a')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link = title_elem.get('href', '')
                        
                        if link and not link.startswith('http'):
                            link = self.base_url + link
                        
                        news_item = {
                            "title": title,
                            "description": "",
                            "link": link,
                            "pub_date": "",
                            "source": "",
                            "category": "기타"
                        }
                        
                        if title and link:
                            news_list.append(news_item)
                            
                except Exception as e:
                    print(f"뉴스 아이템 크롤링 오류: {str(e)}")
                    continue
            
            return news_list
            
        except Exception as e:
            print(f"뉴스 크롤링 오류: {str(e)}")
            return []
