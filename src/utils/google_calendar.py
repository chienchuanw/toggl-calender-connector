import os
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv, set_key
from dateutil import parser

load_dotenv()
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")


def find_existing_event(
    service: Any, 
    description: str, 
    start_time: str, 
    end_time: str,
    calendar_id: str = GOOGLE_CALENDAR_ID
) -> Optional[Dict[str, Any]]:
    """
    在 Google Calendar 中搜尋特定時間範圍和描述的事件。

    Args:
        service: Google Calendar API 服務實例
        description: 事件描述/標題
        start_time: 事件開始時間，格式為 ISO 格式字串
        end_time: 事件結束時間，格式為 ISO 格式字串
        calendar_id: 要搜尋的日曆 ID

    Returns:
        Optional[Dict[str, Any]]: 如果找到匹配的事件則返回事件詳情，否則返回 None
    """
    # 解析輸入的時間字串
    start_datetime = parser.parse(start_time)
    end_datetime = parser.parse(end_time)
    
    # 設定時間範圍的查詢參數 
    time_min = start_datetime.isoformat()
    time_max = end_datetime.isoformat()
    
    # 查詢該時間範圍內的所有事件
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # 檢查每個事件的標題是否與描述匹配
    for event in events:
        if event.get('summary', '') == description:
            # 標記這是一個已存在的事件
            event['is_existing'] = True
            return event
    
    return None


def create_event(
    service: Any, 
    description: str, 
    start_time: str, 
    end_time: str,
    calendar_id: str = GOOGLE_CALENDAR_ID,
    check_duplicate: bool = True
) -> Optional[Dict[str, Any]]:
    """
    在 Google Calendar 中創建一個新的事件，先檢查是否已存在相同事件。

    Args:
        service: Google Calendar API 服務實例
        description: 事件描述/標題
        start_time: 事件開始時間，格式為 ISO 格式字串
        end_time: 事件結束時間，格式為 ISO 格式字串
        calendar_id: 要使用的日曆 ID
        check_duplicate: 是否檢查重複事件

    Returns:
        Optional[Dict[str, Any]]: 如果成功創建或找到現有事件，則返回事件詳情
    """
    # 如需檢查重複，先搜尋現有事件
    if check_duplicate:
        existing_event = find_existing_event(service, description, start_time, end_time, calendar_id)
        if existing_event:
            print(f"已存在相同事件: {description}，開始時間: {start_time}")
            return existing_event

    # 創建新事件
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
        service.events()
        .insert(calendarId=calendar_id, body=event)
        .execute()
    )
    
    # 標記這是一個新創建的事件
    created_event['is_existing'] = False
    
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
    return calendar_list.get("items", [])


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
