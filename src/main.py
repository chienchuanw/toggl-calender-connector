from clients.toggl_client import togglClient
from clients.google_client import get_calendar_service
from utils.google_calendar import create_event
from datetime import datetime
from typing import List, Dict, Any, Optional

"""
主要程序模塊，用於將 toggl 記錄的時間條目同步到 Google 日曆中。
此模塊會載入今天的 toggl 時間記錄，並將每個記錄在 Google 日曆中創建對應的事件。
"""


def main() -> None:
    """
    主程序入口點，起動同步過程。

    流程：
    1. 初始化 toggl 和 Google Calendar 的客戶端。
    2. 取得今天的日期。
    3. 從 toggl 取得今天的時間記錄。
    4. 將每個時間記錄轉換為 Google 日曆事件。
    """
    client = togglClient()
    service = get_calendar_service()

    today = datetime.today().strftime("%Y-%m-%d")
    entries = client.get_time_entries(today, today)

    for entry in entries:
        description = entry["description"]
        start = entry["start"]
        end = entry["end"]
        create_event(service, description, start, end)


if __name__ == "__main__":
    main()
