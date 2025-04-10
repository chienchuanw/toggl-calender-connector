"""
Google Calendar 日曆管理模組
負責處理日曆列表相關功能
"""

from typing import Any, Dict, List


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
