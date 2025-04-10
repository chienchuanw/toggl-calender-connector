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
        url = f"{self.base_url}/details"
        params = {
            "user_agent": "toggl-calendar-connector",
            "workspace_id": TOGGL_WORKSPACE_ID,
            "since": start_date,
            "until": end_date,
            "order_desc": "off",
        }
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            data = response.json()
            
            # 格式化數據以符合我們的需要
            entries = []
            for entry in data.get("data", []):
                if entry.get("description") and entry.get("start") and entry.get("end"):
                    entries.append({
                        "description": entry.get("description", ""),
                        "start": entry.get("start", ""),
                        "end": entry.get("end", ""),
                        "project": entry.get("project", ""),
                        "client": entry.get("client", ""),
                        "tags": entry.get("tags", []),
                    })
            
            return entries
        except Exception as e:
            print(f"獲取 Toggl 時間條目出錯: {e}")
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
