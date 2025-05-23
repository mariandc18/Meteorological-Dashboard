from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class WeatherHourly(Base):
    __tablename__ = 'weather_hourly'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ubicacion_id = Column(String, nullable=False)
    date = Column(DateTime, nullable=False, primary_key=True)
    time = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    relative_humidity = Column(Float, nullable=False)
    dew_point = Column(Float, nullable=False)
    apparent_temperature = Column(Float, nullable=False)
    precipitation = Column(Float, nullable=False)
    cloud_cover = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_gusts = Column(Float, nullable=False)
    wind_direction = Column(Float, nullable=False)
    snowfall = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    is_day = Column(Integer, nullable=False)

class WeatherDaily(Base):
    __tablename__ = 'weather_daily'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ubicacion_id = Column(String, nullable=False)
    date = Column(DateTime, nullable=False, primary_key=True)
    temperature_mean = Column(Float, nullable=False)
    temperature_max = Column(Float, nullable=False)
    temperature_min = Column(Float, nullable=False)
    sunrise = Column(String, nullable=False)
    sunset = Column(String, nullable=False)
    precipitation_sum = Column(Float, nullable=False)
    snowfall_sum = Column(Float, nullable=False)
    wind_speed_10m_max = Column(Float, nullable=False)
