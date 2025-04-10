import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

TOGGL_API_TOKEN = os.getenv("TOGGL_API_TOKEN")
TOGGL_WORKSPACE_ID = os.getenv("TOGGL_WORKSPACE_ID")

class TogglClient:
    """
    Toggl API 客戶端，用於獲取時間追蹤記錄。
    """

    def __init__(self):
        """
        初始化 Toggl 客戶端，設置認證和基礎 URL。
        """
        if not TOGGL_API_TOKEN:
            raise ValueError("缺少 TOGGL_API_TOKEN 環境變數")
        
        if not TOGGL_WORKSPACE_ID:
            raise ValueError("缺少 TOGGL_WORKSPACE_ID 環境變數")
        
        self.auth = (TOGGL_API_TOKEN, "api_token")
        self.base_url = f"https://api.track.toggl.com/reports/api/v2/workspace/{TOGGL_WORKSPACE_ID}"
        self.api_url = "https://api.track.toggl.com/api/v9"
        
    def get_time_entries(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        從 Toggl 獲取指定日期範圍內的時間記錄。

        Args:
            start_date: 開始日期，格式為 'YYYY-MM-DD'
            end_date: 結束日期，格式為 'YYYY-MM-DD'

        Returns:
            list: 時間記錄列表，每條記錄包含描述、開始時間和結束時間等信息
            如果請求失敗則返回空列表
        """
        print(f"獲取時間條目：從 {start_date} 到 {end_date}")
        
        # 根據 Toggl API v9 文檔，正確的端點是 /me/time_entries
        url = f"{self.api_url}/me/time_entries"
        
        try:
            # 首先獲取所有時間條目
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            all_entries = response.json()
            
            # 將開始和結束日期轉換為 datetime 對象，便於比較
            from datetime import datetime
            
            # 更寬容的日期處理，支援多種日期格式
            try:
                # 嘗試直接解析
                start_dt = datetime.fromisoformat(f"{start_date}T00:00:00+00:00")
                end_dt = datetime.fromisoformat(f"{end_date}T23:59:59+00:00")
            except ValueError:
                # 如果失敗，嘗試其它格式
                from dateutil import parser
                start_dt = parser.parse(f"{start_date} 00:00:00")
                end_dt = parser.parse(f"{end_date} 23:59:59")
            
            # 格式化數據以符合我們的需要
            entries = []
            for entry in all_entries:
                # 跳過沒有結束時間的條目（當前正在進行的）
                if entry.get("duration", 0) < 0:
                    continue
                    
                description = entry.get("description", "")
                start_str = entry.get("start", "")
                stop_str = entry.get("stop", "")
                
                if not (description and start_str and stop_str):
                    continue
                
                # 解析時間條目的開始和結束時間
                try:
                    entry_start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    entry_stop = datetime.fromisoformat(stop_str.replace('Z', '+00:00'))
                    
                    # 檢查時間條目是否在指定的日期範圍內
                    if entry_start <= end_dt and entry_stop >= start_dt:
                        # 獲取項目信息（如果有）
                        project_name = None
                        project_id = entry.get("project_id")
                        
                        if project_id:
                            try:
                                project_url = f"{self.api_url}/workspaces/{TOGGL_WORKSPACE_ID}/projects/{project_id}"
                                project_response = requests.get(project_url, auth=self.auth)
                                if project_response.status_code == 200:
                                    project_data = project_response.json()
                                    project_name = project_data.get("name")
                            except Exception:
                                pass
                        
                        entries.append({
                            "description": description,
                            "start": start_str,
                            "end": stop_str,  # v9 API 使用 "stop" 而不是 "end"
                            "project": project_name or "",
                            "client": "",  # V9 API 需要額外查詢客戶端信息
                            "tags": entry.get("tags", []),
                        })
                except (ValueError, TypeError):
                    # 跳過無法解析時間的條目
                    continue
            
            print(f"找到 {len(entries)} 個時間條目")
            return entries
        except Exception as e:
            print(f"獲取 Toggl 時間條目出錯: {e}")
            print(f"請求 URL: {url}")
            # 需要更多的試驗信息嗎？可以使用以下代碼
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"響應內容: {e.response.text[:500]}...")
            
            # 測試基本連線
            try:
                test_url = f"{self.api_url}/me"
                test_response = requests.get(test_url, auth=self.auth)
                print(f"帳號測試: {test_response.status_code}")
                if test_response.status_code != 200:
                    print(f"帳號測試失敗! 可能是 API 令牌或認證問題")
            except Exception as test_err:
                print(f"帳號測試出錯: {test_err}")
                
            return []
    
    def get_current_time_entry(self) -> Optional[Dict[str, Any]]:
        """
        獲取當前正在記錄的 Toggl 時間條目。

        Returns:
            Optional[Dict[str, Any]]: 當前正在記錄的時間條目
            如果沒有正在記錄的條目或請求失敗則返回 None
        """
        url = f"{self.api_url}/me/time_entries/current"
        
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            
            # 檢查是否有正在進行的時間條目
            if response.status_code == 200:
                data = response.json()
                
                # 如果沒有正在進行的時間條目，data 可能為 None 或空字典
                if not data:
                    return None
                
                # 獲取項目信息（如果有）
                project_name = None
                workspace_id = data.get("workspace_id")
                project_id = data.get("project_id")
                
                if project_id:
                    project_url = f"{self.api_url}/workspaces/{workspace_id}/projects/{project_id}"
                    try:
                        project_response = requests.get(project_url, auth=self.auth)
                        if project_response.status_code == 200:
                            project_data = project_response.json()
                            project_name = project_data.get("name")
                    except:
                        pass
                
                # 格式化返回數據
                return {
                    "id": data.get("id"),
                    "description": data.get("description", ""),
                    "start": data.get("start", ""),
                    "duration": data.get("duration", 0),  # 負數表示正在進行
                    "project": project_name,
                    "project_id": project_id,
                    "workspace_id": workspace_id,
                    "tags": data.get("tags", []),
                    "billable": data.get("billable", False)
                }
            
            return None
        except Exception as e:
            print(f"獲取當前 Toggl 時間條目出錯: {e}")
            return None
    
    def stop_current_time_entry(self) -> bool:
        """
        停止當前正在記錄的 Toggl 時間條目。

        Returns:
            bool: 是否成功停止計時
        """
        url = f"{self.api_url}/me/time_entries/current/stop"
        
        try:
            response = requests.patch(url, auth=self.auth)
            response.raise_for_status()
            
            return response.status_code == 200
        except Exception as e:
            print(f"停止當前 Toggl 時間條目出錯: {e}")
            return False
