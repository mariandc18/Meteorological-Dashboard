from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ForecastData:
    date: datetime
    temperature: Optional[float] = None
    apparent_temperature: Optional[float] = None
    humidity: Optional[float] = None
    dew_point: Optional[float] = None
    cloud_cover: Optional[float] = None
    precipitation_prob: Optional[float] = None
    rain_intensity: Optional[float] = None
    snow_intensity: Optional[float] = None
    hail_probability: Optional[float] = None
    hail_size: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_gust: Optional[float] = None
    wind_direction: Optional[float] = None
    pressure_sea_level: Optional[float] = None
    pressure_surface_level: Optional[float] = None
    uv_index: Optional[float] = None
    visibility: Optional[float] = None
    weather_code: Optional[int] = None
    description: Optional[str] = None 
    source_name: str = ""        

@dataclass
class Location:
    name: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
