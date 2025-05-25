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
    
class Cyclones(Base):
    __tablename__ = 'cyclones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sid = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    season = Column(Integer, nullable=False)
    iso_time = Column(DateTime, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    usa_status = Column(String(50), nullable=False)
    usa_wind = Column(Integer, nullable=False)
    usa_pres = Column(Integer, nullable=False)
    usa_sshs = Column(Integer, nullable=False)
    usa_r34_ne = Column(Integer, nullable=True)
    usa_r34_se = Column(Integer, nullable=True)
    usa_r34_sw = Column(Integer, nullable=True)
    usa_r34_nw = Column(Integer, nullable=True)
    usa_roci = Column(Integer, nullable=True)
    usa_poci = Column(Integer, nullable=True)
    dist2land = Column(Float, nullable=False)
    landfall = Column(Integer, nullable=True)