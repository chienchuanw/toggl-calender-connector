# src/toggl_client.py

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOGGL_API_TOKEN = os.getenv("TOGGL_API_TOKEN")
TOGGL_WORKSPACE_ID = os.getenv("TOGGL_WORKSPACE_ID")


class TogglClient:
    def __init__(self):
        self.auth = (TOGGL_API_TOKEN, "api_token")
        self.base_url = "https://api.track.toggl.com/reports/api/v2"

    def get_time_entries(self, start_date: str, end_date: str):
        url = f"{self.base_url}/details"
        params = {
            "workspace_id": TOGGL_WORKSPACE_ID,
            "since": start_date,
            "until": end_date,
            "user_agent": "toggl-to-gcal-script",
        }

        response = requests.get(url, auth=self.auth, params=params)

        if response.status_code == 200:
            return response.json()["data"]
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []


# 範例測試
if __name__ == "__main__":
    client = TogglClient()
    today = datetime.today().strftime("%Y-%m-%d")
    data = client.get_time_entries(today, today)
    print(f"There are {len(data)} entries today:")
    for entry in data:
        print(entry)
