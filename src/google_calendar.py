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
