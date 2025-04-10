"""
Google Calendar 工具

此檔案保留向後兼容性，主要功能已重構至 google_calendar/ 模組
"""

# 從重構後的模組導入所有函數和變數
from .google_calendar.events import find_existing_event, create_event
from .google_calendar.calendars import list_calendars
from .google_calendar.settings import update_calendar_id, GOOGLE_CALENDAR_ID
