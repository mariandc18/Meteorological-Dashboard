import requests
from typing import List
from datetime import datetime
from models.forecast import ForecastData, Location

class VisualCrossingProvider():
    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_forecast(self, location: Location) -> List[ForecastData]:
        if not location.name:
            raise ValueError("Visual Crossing requiere el nombre de la ciudad como ubicación.")

        params = {
            "unitGroup": "metric",  
            "elements": ",".join([
                "datetime", "temp", "feelslike", "dew", "humidity",
                "precip", "precipprob", "snow", "windgust", "windspeed",
                "winddir", "pressure", "cloudcover", "visibility", "uvindex"
            ]),
            "include": "hours",
            "key": self.api_key,
            "contentType": "json"
        }

        url = f"{self.BASE_URL}/{location.name}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        for day in data.get("days", []):
            day_date = day.get("datetime") 
            for hour in day.get("hours", []):
                time_str = hour.get("datetime") 
                full_datetime = f"{day_date}T{time_str}" 
        
                forecasts.append(ForecastData(
                    date=datetime.fromisoformat(full_datetime),
                    temperature=hour.get("temp"),
                    apparent_temperature=hour.get("feelslike"),
                    dew_point=hour.get("dew"),
                    humidity=hour.get("humidity"),
                    precipitation_prob=hour.get("precipprob"),
                    rain_intensity=hour.get("precip"),
                    snow_intensity=hour.get("snow"),
                    cloud_cover=hour.get("cloudcover"),
                    wind_speed=hour.get("windspeed"),
                    wind_gust=hour.get("windgust"),
                    wind_direction=hour.get("winddir"),
                    pressure_sea_level=hour.get("pressure"),
                    visibility=hour.get("visibility"),
                    uv_index=hour.get("uvindex"),
                    source_name="Visual Crossing"
                ))
        return forecasts
