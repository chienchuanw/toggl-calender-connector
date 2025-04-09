# src/google_calendar.py

import os
import datetime
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")


def get_calendar_service():
    """
    建立和返回 Google Calendar API 服務實例。
    
    流程：
    1. 如果本地存在 token.json 檔案，則載入現有認證。
    2. 否則，啟動 OAuth2 授權流程以取得新的權限。
    3. 將新的驗證權戶儲存至 token.json 檔案。
    
    Returns:
        object: 已建立的 Google Calendar API 服務實例
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def create_event(service, description, start_time, end_time):
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
