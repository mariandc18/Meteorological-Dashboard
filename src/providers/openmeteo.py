from datetime import datetime
from typing import List
from models.forecast import ForecastData, Location
import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry

class OpenMeteoProvider():
    GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self):
        cache = requests_cache.CachedSession('.cache', expire_after=3600)
        session = retry(cache, retries=3, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=session)

    def fetch_forecast(self, location: Location) -> List[ForecastData]:
        lat, lon = self._obtain_coordinates(location)

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": [
                "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "snowfall", "cloud_cover", "weather_code", "wind_speed_10m",
                "wind_gusts_10m", "visibility", "precipitation_probability", "rain", "wind_direction_10m", "pressure_msl", "surface_pressure", "uv_index"]
        }

        url = "https://api.open-meteo.com/v1/forecast"
        responses = self.client.weather_api(url, params=params)
        response = responses[0]
        hourly = response.Hourly()

        times = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )

        return [
            ForecastData(
                date=t.to_pydatetime(),
                temperature=hourly.Variables(0).ValuesAsNumpy()[i],
                humidity=hourly.Variables(1).ValuesAsNumpy()[i],
                dew_point=hourly.Variables(2).ValuesAsNumpy()[i],
                apparent_temperature=hourly.Variables(3).ValuesAsNumpy()[i],
                rain_intensity=hourly.Variables(4).ValuesAsNumpy()[i],
                snow_intensity=hourly.Variables(5).ValuesAsNumpy()[i],
                cloud_cover=hourly.Variables(6).ValuesAsNumpy()[i],
                weather_code=int(hourly.Variables(7).ValuesAsNumpy()[i]),
                wind_speed=hourly.Variables(8).ValuesAsNumpy()[i],
                wind_gust=hourly.Variables(9).ValuesAsNumpy()[i],
                visibility=hourly.Variables(10).ValuesAsNumpy()[i],
                precipitation_prob=hourly.Variables(11).ValuesAsNumpy()[i],
                wind_direction=hourly.Variables(13).ValuesAsNumpy()[i],
                pressure_sea_level=hourly.Variables(14).ValuesAsNumpy()[i],
                pressure_surface_level=hourly.Variables(15).ValuesAsNumpy()[i],
                uv_index=hourly.Variables(16).ValuesAsNumpy()[i],
                source_name="Open-Meteo"
            )
            for i, t in enumerate(times)
        ]

    def _obtain_coordinates(self, location: Location) -> tuple[float, float]:
        if location.lat is not None and location.lon is not None:
            return location.lat, location.lon
        elif location.name:
            params = {"name": location.name, "count": 1, "format": "json", "language": "en"}
            response = requests.get(self.GEO_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("results"):
                coords = data["results"][0]
                return coords["latitude"], coords["longitude"]
            raise ValueError(f"No se encontraron coordenadas para '{location.name}'")
        else:
            raise ValueError("Se requiere el nombre o las coordenadas del lugar.")    