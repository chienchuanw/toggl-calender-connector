from datetime import datetime
import pytz
import pyfiglet


def format_time_display(time_str: str) -> str:
    """
    將 ISO 時間字串格式化為 Taiwan 時區的可讀格式。
    """
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        dt_taiwan = dt.astimezone(pytz.timezone("Asia/Taipei"))
        return dt_taiwan.strftime("%Y-%m-%d %I:%M:%S %p")
    except Exception:
        return time_str


def calculate_duration(start: str, end: str) -> str:
    """
    計算兩個 ISO 時間字串間的持續時間。
    """
    try:
        s = datetime.fromisoformat(start.replace("Z", "+00:00"))
        e = datetime.fromisoformat(end.replace("Z", "+00:00"))
        total_seconds = int((e - s).total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except Exception:
        return "--:--:--"


def generate_header(text: str, font: str = "slant") -> str:
    """
    產生 ASCII 標題字。
    """
    try:
        return pyfiglet.figlet_format(text, font=font)
    except Exception:
        return pyfiglet.figlet_format(text)
