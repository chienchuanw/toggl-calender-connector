import os

GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")


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
