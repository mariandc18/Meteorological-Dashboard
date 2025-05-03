from datetime import datetime
from zoneinfo import ZoneInfo

def convert_time_WheatherAPI(s: str) -> str:
    s = s.strip()
    dt = datetime.strptime(s, '%I:%M %p')
    return dt.strftime('%H:%M')

def convert_time_OpenMeteoAPI(ts: float, tz: str = None) -> str:
    tz_info = ZoneInfo(tz) if tz else None
    dt = datetime.fromtimestamp(ts, tz=tz_info)
    return dt.strftime('%H:%M')

def split_datetime(date):
    date_str = date.strftime('%Y-%m-%d')
    time_str = date.strftime('%H:%M:%S')
    return date_str, time_str
