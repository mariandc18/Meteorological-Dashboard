from datetime import date
from typing import Optional, List
from upstash_redis import Redis
import json
from src.chatbot.models.forecast import ForecastData
from datetime import datetime
import numpy as np

redis = Redis.from_env()
TTL_SECONDS = 86400  

def _get_cache_key(location: str) -> str:
    return f"forecast:{location.lower()}:{date.today().isoformat()}"

def serialize_forecasts(forecasts: List[ForecastData]) -> str:
    def clean(obj):
        d = obj.__dict__.copy()
        if isinstance(d["date"], datetime):
            d["date"] = d["date"].isoformat()

        for k, v in d.items():
            if isinstance(v, (np.generic, np.float32, np.float64)):
                d[k] = float(v)
        return d
    return json.dumps([clean(f) for f in forecasts], ensure_ascii=False)

def deserialize_forecasts(raw: str) -> List[ForecastData]:
    from datetime import datetime
    data = json.loads(raw)
    return [
        ForecastData(
            **{
                **item,
                "date": datetime.fromisoformat(item["date"])
            }
        )
        for item in data
    ]

def save_forecast(location: str, data: List[ForecastData]):
    key = _get_cache_key(location)
    value = serialize_forecasts(data)
    redis.setex(key, TTL_SECONDS, value)

def get_forecast(location: str) -> Optional[List[ForecastData]]:
    key = _get_cache_key(location)
    raw = redis.get(key)
    return deserialize_forecasts(raw) if raw else None
