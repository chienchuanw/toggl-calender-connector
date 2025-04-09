import os
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv, set_key

load_dotenv()
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")


def create_event(service: Any, description: str, start_time: str, end_time: str) -> Optional[Dict[str, Any]]:
    """
    在 Google Calendar 中創建一個新的事件。

    Args:
        service: Google Calendar API 服務實例
        description: 事件描述/標題
        start_time: 事件開始時間，格式為 ISO 格式字串
        end_time: 事件結束時間，格式為 ISO 格式字串

    Returns:
        None: 如果成功創建事件，會在控制台列印確認信息
    """
    event = {
        "summary": description,
        "start": {
            "dateTime": start_time,
            "timeZone": "Asia/Taipei",
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Taipei",
        },
    }
    created_event = (
        service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
    )
    print(
        f"Created event: {created_event.get('summary')} @ {created_event.get('start').get('dateTime')}"
    )
    return created_event


def list_calendars(service: Any) -> List[Dict[str, Any]]:
    """
    獲取用戶的所有日曆清單。

    Args:
        service: Google Calendar API 服務實例

    Returns:
        List[Dict[str, Any]]: 日曆列表，每個日曆包含 id, summary, primary 等信息
    """
    calendar_list = service.calendarList().list().execute()
    return calendar_list.get('items', [])


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
        env_path = os.path.join(os.getcwd(), '.env')
        set_key(env_path, "GOOGLE_CALENDAR_ID", calendar_id)
        
        # 更新當前環境變數
        global GOOGLE_CALENDAR_ID
        GOOGLE_CALENDAR_ID = calendar_id
        
        return True
    except Exception as e:
        print(f"更新 .env 文件時出錯: {str(e)}")
        return False
