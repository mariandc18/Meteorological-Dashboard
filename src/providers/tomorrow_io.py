import requests
from datetime import datetime
from typing import List
from models.forecast import ForecastData, Location
#from src.providers.weather_provider import WeatherProvider

class TomorrowProvider():
    BASE_URL = "https://api.tomorrow.io/v4/weather/forecast"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_forecast(self, location: Location) -> List[ForecastData]:
        location_param = self._resolve_location_param(location)

        params = {
            "location": location_param,
            "apikey": self.api_key,
            "fields": ",".join([
                "temperature", "temperatureApparent", "humidity", "dewPoint",
                "cloudCover", "cloudBase", "cloudCeiling",
                "precipitationProbability", "rainIntensity", "snowIntensity",
                "hailProbability", "hailSize",
                "windSpeed", "windGust", "windDirection",
                "pressureSeaLevel", "pressureSurfaceLevel",
                "uvIndex", "visibility", "weatherCode"
            ]),
            "units": "metric",
            "timesteps": "1h"
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        hourly_data = data["timelines"].get("hourly", [])

        forecasts: List[ForecastData] = []
        for item in hourly_data:
            values = item.get("values", {})
            forecasts.append(
                ForecastData(
                    date=datetime.fromisoformat(item["time"].replace("Z", "+00:00")),
                    temperature=values.get("temperature"),
                    apparent_temperature=values.get("temperatureApparent"),
                    humidity=values.get("humidity"),
                    dew_point=values.get("dewPoint"),
                    cloud_cover=values.get("cloudCover"),
                    precipitation_prob=values.get("precipitationProbability"),
                    rain_intensity=values.get("rainIntensity"),
                    snow_intensity=values.get("snowIntensity"),
                    hail_probability=values.get("hailProbability"),
                    hail_size=values.get("hailSize"),
                    wind_speed=values.get("windSpeed"),
                    wind_gust=values.get("windGust"),
                    wind_direction=values.get("windDirection"),
                    pressure_sea_level=values.get("pressureSeaLevel"),
                    pressure_surface_level=values.get("pressureSurfaceLevel"),
                    uv_index=values.get("uvIndex"),
                    visibility=values.get("visibility"),
                    weather_code=values.get("weatherCode"),
                    source_name="Tomorrow.io"
                )
            )
        return forecasts

    def _resolve_location_param(self, location: Location) -> str:
        if location.name:
            return location.name
        elif location.lat is not None and location.lon is not None:
            return f"{location.lat},{location.lon}"
        else:
            raise ValueError("Debe proporcionar al menos el nombre o las coordenadas del lugar.")
    
