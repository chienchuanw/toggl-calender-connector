import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


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
