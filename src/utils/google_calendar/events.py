"""
Google Calendar 事件處理模組
負責處理事件相關功能，如尋找和建立事件
"""

from typing import Any, Dict, Optional
from dateutil import parser

# 從設定模組導入共用變數
from .settings import GOOGLE_CALENDAR_ID


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
