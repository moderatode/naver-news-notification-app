#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설정 관리 모듈
- 앱 설정 저장/로드
- JSON 파일 기반 설정 관리
- 기본값 제공
"""

import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "count": 5,
            "sort": "최신",
            "schedule_mode": "interval",
            "interval": 1,
            "alarm_times": "08:30,12:00,18:00",
            "weekdays": {
                "월": True,
                "화": True,
                "수": True,
                "목": True,
                "금": True,
                "토": False,
                "일": False
            },
            "naver_client_id": "",
            "naver_client_secret": "",
            "kakao_client_id": "",
            "auto_start": False,
            "minimize_to_tray": True,
            "log_level": "INFO"
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        설정 파일 로드
        
        Returns:
            설정 딕셔너리
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 기본값과 병합
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            else:
                # 기본 설정으로 새 파일 생성
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            print(f"설정 로드 오류: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        설정 파일 저장
        
        Args:
            config: 저장할 설정 딕셔너리
        
        Returns:
            저장 성공 여부
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"설정 저장 오류: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        특정 설정값 가져오기
        
        Args:
            key: 설정 키
            default: 기본값
        
        Returns:
            설정값
        """
        config = self.load_config()
        return config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        특정 설정값 설정
        
        Args:
            key: 설정 키
            value: 설정값
        
        Returns:
            설정 성공 여부
        """
        try:
            config = self.load_config()
            config[key] = value
            return self.save_config(config)
        except Exception as e:
            print(f"설정 변경 오류: {str(e)}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        여러 설정값 한번에 업데이트
        
        Args:
            updates: 업데이트할 설정 딕셔너리
        
        Returns:
            업데이트 성공 여부
        """
        try:
            config = self.load_config()
            config.update(updates)
            return self.save_config(config)
        except Exception as e:
            print(f"설정 업데이트 오류: {str(e)}")
            return False
    
    def reset_to_default(self) -> bool:
        """
        설정을 기본값으로 리셋
        
        Returns:
            리셋 성공 여부
        """
        try:
            return self.save_config(self.default_config)
        except Exception as e:
            print(f"설정 리셋 오류: {str(e)}")
            return False
    
    def backup_config(self, backup_file: str = None) -> bool:
        """
        설정 백업
        
        Args:
            backup_file: 백업 파일명 (기본값: config_backup_YYYYMMDD_HHMMSS.json)
        
        Returns:
            백업 성공 여부
        """
        try:
            if not backup_file:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"config_backup_{timestamp}.json"
            
            config = self.load_config()
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"설정이 {backup_file}로 백업되었습니다.")
            return True
        except Exception as e:
            print(f"설정 백업 오류: {str(e)}")
            return False
    
    def restore_config(self, backup_file: str) -> bool:
        """
        설정 복원
        
        Args:
            backup_file: 복원할 백업 파일명
        
        Returns:
            복원 성공 여부
        """
        try:
            if not os.path.exists(backup_file):
                print(f"백업 파일을 찾을 수 없습니다: {backup_file}")
                return False
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return self.save_config(config)
        except Exception as e:
            print(f"설정 복원 오류: {str(e)}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, list]:
        """
        설정 유효성 검사
        
        Args:
            config: 검사할 설정 딕셔너리
        
        Returns:
            (유효성 여부, 오류 메시지 리스트)
        """
        errors = []
        
        try:
            # 필수 필드 검사
            required_fields = ["count", "sort", "schedule_mode"]
            for field in required_fields:
                if field not in config:
                    errors.append(f"필수 필드 누락: {field}")
            
            # count 검사
            if "count" in config:
                count = config["count"]
                if not isinstance(count, int) or count < 1 or count > 20:
                    errors.append("count는 1-20 사이의 정수여야 합니다.")
            
            # sort 검사
            if "sort" in config:
                sort = config["sort"]
                if sort not in ["최신", "관련도"]:
                    errors.append("sort는 '최신' 또는 '관련도'여야 합니다.")
            
            # schedule_mode 검사
            if "schedule_mode" in config:
                mode = config["schedule_mode"]
                if mode not in ["interval", "alarm"]:
                    errors.append("schedule_mode는 'interval' 또는 'alarm'이어야 합니다.")
            
            # interval 검사
            if "interval" in config:
                interval = config["interval"]
                if not isinstance(interval, int) or interval < 1 or interval > 24:
                    errors.append("interval은 1-24 사이의 정수여야 합니다.")
            
            # alarm_times 검사
            if "alarm_times" in config:
                times = config["alarm_times"]
                if isinstance(times, str):
                    time_list = [t.strip() for t in times.split(",")]
                    for time_str in time_list:
                        try:
                            hour, minute = map(int, time_str.split(":"))
                            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                                errors.append(f"잘못된 시간 형식: {time_str}")
                        except ValueError:
                            errors.append(f"잘못된 시간 형식: {time_str}")
            
            # weekdays 검사
            if "weekdays" in config:
                weekdays = config["weekdays"]
                if isinstance(weekdays, dict):
                    valid_days = ["월", "화", "수", "목", "금", "토", "일"]
                    for day, value in weekdays.items():
                        if day not in valid_days:
                            errors.append(f"잘못된 요일: {day}")
                        if not isinstance(value, bool):
                            errors.append(f"요일 값은 boolean이어야 합니다: {day}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"설정 검사 오류: {str(e)}")
            return False, errors
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        설정 정보 가져오기
        
        Returns:
            설정 정보 딕셔너리
        """
        try:
            config = self.load_config()
            return {
                "config_file": self.config_file,
                "file_exists": os.path.exists(self.config_file),
                "file_size": os.path.getsize(self.config_file) if os.path.exists(self.config_file) else 0,
                "config_keys": list(config.keys()),
                "is_valid": self.validate_config(config)[0]
            }
        except Exception as e:
            print(f"설정 정보 가져오기 오류: {str(e)}")
            return {}
