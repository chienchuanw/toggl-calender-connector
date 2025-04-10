"""
Google Calendar 設定處理模組
負責處理設定相關的功能，如更新日曆ID等
"""

import os
from typing import Any
from dotenv import load_dotenv, set_key

# 載入環境變數
load_dotenv()
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")


def update_calendar_id(calendar_id: str) -> bool:
    """
    更新 .env 文件中的 GOOGLE_CALENDAR_ID 值

    Args:
        calendar_id: 要設置的日曆 ID

    Returns:
        bool: 是否成功更新 .env 文件
    """
    try:
        # 使用 dotenv 的 set_key 函數更新 .env 文件
        env_path = os.path.join(os.getcwd(), ".env")
        set_key(env_path, "GOOGLE_CALENDAR_ID", calendar_id)

        # 更新當前環境變數
        global GOOGLE_CALENDAR_ID
        GOOGLE_CALENDAR_ID = calendar_id

        return True
    except Exception as e:
        print(f"更新 .env 文件時出錯: {str(e)}")
        return False
