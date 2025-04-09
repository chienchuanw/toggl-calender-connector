import os
import requests
from dotenv import load_dotenv
from datetime import datetime

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
        self.auth = (TOGGL_API_TOKEN, "api_token")
        self.base_url = "https://api.track.toggl.com/reports/api/v2"

    def get_time_entries(self, start_date: str, end_date: str):
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
            "workspace_id": TOGGL_WORKSPACE_ID,
            "since": start_date,
            "until": end_date,
            "user_agent": "toggl-to-gcal-script",
        }

        response = requests.get(url, auth=self.auth, params=params)

        if response.status_code == 200:
            return response.json()["data"]
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []
