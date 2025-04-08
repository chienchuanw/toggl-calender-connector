from src.toggl_client import TogglClient
from src.google_calendar import get_calendar_service, create_event
from datetime import datetime

client = TogglClient()
service = get_calendar_service()

today = datetime.today().strftime("%Y-%m-%d")
entries = client.get_time_entries(today, today)

for entry in entries:
    description = entry["description"]
    start = entry["start"]
    end = entry["end"]
    create_event(service, description, start, end)
