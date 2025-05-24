import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
from src.storage.tables import WeatherDaily, WeatherHourly, Base
from transformation import convert_time_OpenMeteoAPI, round_to_two_decimals 
from src.storage.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
def check_hypertable_exists(table_name):
    query = f"SELECT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = '{table_name}');"
    result = session.execute(text(query)).scalar()
    return result 

if not check_hypertable_exists("weather_hourly"):
    session.execute(text("SELECT create_hypertable('weather_hourly', 'date');"))

if not check_hypertable_exists("weather_daily"):
    session.execute(text("SELECT create_hypertable('weather_daily', 'date');"))

session.commit()

cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://archive-api.open-meteo.com/v1/archive"

def check_existing_data(location, start_date, end_date):
    query_hourly = text(f"""
        SELECT COUNT(*) FROM weather_hourly
        WHERE ubicacion_id = '{location["_id"]}' 
        AND date BETWEEN '{start_date}' AND '{end_date}'
    """)

    query_daily = text(f"""
        SELECT COUNT(*) FROM weather_daily
        WHERE ubicacion_id = '{location["_id"]}' 
        AND date BETWEEN '{start_date}' AND '{end_date}'
    """)

    result_hourly = session.execute(query_hourly).scalar()
    result_daily = session.execute(query_daily).scalar()

    if result_hourly > 0 and result_daily > 0:
        print(f"Datos ya existen para {location['municipality']}. Saltando API.")
        return True  

    return False 

def process_location(location):
    start_date = "2025-05-02"
    end_date = "2000-01-01"
    
    if check_existing_data(location, start_date, end_date):
        return [], [] 
    
    params = {
        "latitude": location["location"]["coordinates"][1],
        "longitude": location["location"]["coordinates"][0],
        "start_date": start_date,
        "end_date": end_date, 
        "daily": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset",
                  "precipitation_sum", "snowfall_sum", "wind_speed_10m_max"],
        "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
                   "precipitation", "cloud_cover", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m",
                   "snowfall", "pressure_msl", "is_day"]
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly_data, daily_data = transformar_datos(response, location)
    return hourly_data, daily_data

def transformar_datos(response, location):
    hourly = response.Hourly()
    hourly_dates = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    hourly_data = [
        {
            "ubicacion_id": str(location["_id"]),
            "date": hourly_dates[i],
            "time": hourly_dates[i].strftime("%H:%M:%S"),
            "temperature": round_to_two_decimals(hourly.Variables(0).ValuesAsNumpy()[i].item()),
            "relative_humidity": round_to_two_decimals(hourly.Variables(1).ValuesAsNumpy()[i].item()),
            "dew_point": round_to_two_decimals(hourly.Variables(2).ValuesAsNumpy()[i].item()),
            "apparent_temperature": round_to_two_decimals(hourly.Variables(3).ValuesAsNumpy()[i].item()),
            "precipitation": round_to_two_decimals(hourly.Variables(4).ValuesAsNumpy()[i].item()),
            "cloud_cover": round_to_two_decimals(hourly.Variables(5).ValuesAsNumpy()[i].item()),
            "wind_speed": round_to_two_decimals(hourly.Variables(6).ValuesAsNumpy()[i].item()),
            "wind_gusts": round_to_two_decimals(hourly.Variables(7).ValuesAsNumpy()[i].item()),
            "wind_direction": round_to_two_decimals(hourly.Variables(8).ValuesAsNumpy()[i].item()),
            "snowfall": round_to_two_decimals(hourly.Variables(9).ValuesAsNumpy()[i].item()),
            "pressure": round_to_two_decimals(hourly.Variables(10).ValuesAsNumpy()[i].item()),
            "is_day": int(hourly.Variables(11).ValuesAsNumpy()[i]) 
        }
        for i in range(len(hourly_dates))
    ]

    daily = response.Daily()
    daily_dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )

    daily_data = [
        {
            "ubicacion_id": str(location["_id"]),
            "date": daily_dates[i],
            "temperature_mean": round_to_two_decimals(daily.Variables(0).ValuesAsNumpy()[i].item()),
            "temperature_max": round_to_two_decimals(daily.Variables(1).ValuesAsNumpy()[i].item()),
            "temperature_min": round_to_two_decimals(daily.Variables(2).ValuesAsNumpy()[i].item()),
            "sunrise": convert_time_OpenMeteoAPI(daily.Variables(3).ValuesInt64AsNumpy()[i]),
            "sunset": convert_time_OpenMeteoAPI(daily.Variables(4).ValuesInt64AsNumpy()[i]),
            "precipitation_sum": round_to_two_decimals(daily.Variables(5).ValuesAsNumpy()[i].item()),
            "snowfall_sum": round_to_two_decimals(daily.Variables(6).ValuesAsNumpy()[i].item()),
            "wind_speed_10m_max": round_to_two_decimals(daily.Variables(7).ValuesAsNumpy()[i].item())
        }
        for i in range(len(daily_dates))
    ]
    return hourly_data, daily_data

def get_locations_from_db():
    query = "SELECT id, municipality, latitude, longitude FROM locations;"
    result = session.execute(text(query)).fetchall()

    locations = [
        {
            "_id": str(row[0]), 
            "municipality": row[1], 
            "location": {"coordinates": [row[2], row[3]]}  
        }
        for row in result
    ]
    return locations

def bulk_insert_in_batches(session, model, data, batch_size=400):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        try:
            session.bulk_insert_mappings(model, batch)
            session.commit()
        except OperationalError:
            print("Conexión perdida. Reintentando en 5 segundos...")
            time.sleep(5)
            session.rollback()
            session.bulk_insert_mappings(model, batch)
            session.commit() 

locations = get_locations_from_db()
for idx, location in enumerate(locations):
    if idx % 10 == 0:
        print("Espere 15 minutos para evitar sobrecarga de la API...")
        time.sleep(15)

    hourly_data, daily_data = process_location(location)
    if hourly_data:
        bulk_insert_in_batches(session, WeatherHourly, hourly_data)
    if daily_data:
        bulk_insert_in_batches(session, WeatherDaily, daily_data)
    session.commit()
    print(f"Datos almacenados correctamente para {location['municipality']}.")

session.close()