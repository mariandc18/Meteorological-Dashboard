import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pymongo import MongoClient
from datetime import datetime
from src.transformation.transformation import convert_time_OpenMeteoAPI, split_datetime
from src.storage.db_manager import MongoDBManager
import time


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Conexión a MongoDB
locations_collection = MongoDBManager(db_name="weather_db", collection_name="locations")
weather_hourly_collection = MongoDBManager(db_name="weather_db", collection_name="weather_hourly")
weather_daily_collection = MongoDBManager(db_name="weather_db", collection_name="weather_daily")

# Crear índices optimizados para cada colección
weather_hourly_collection.collection.create_index([("ubicacion_id", 1), ("date", 1), ("time", 1)], background=True)
weather_daily_collection.collection.create_index([("ubicacion_id", 1), ("date", 1)], background=True)

# API base URL
url = "https://archive-api.open-meteo.com/v1/archive"

def process_location(location):
    params = {
        "latitude": location["location"]["coordinates"][1],
        "longitude": location["location"]["coordinates"][0],
        "start_date": "2020-01-01",
        "end_date": "2023-01-01", 
        "daily": [
            "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
            "sunrise", "sunset", "precipitation_sum", "snowfall_sum", "wind_speed_10m_max"
        ],
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "dew_point_2m",
            "apparent_temperature", "precipitation", "cloud_cover",
            "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m",
            "snowfall", "pressure_msl", "is_day"
        ]
    }

    print(f"\nProcesando datos para {location['municipio']}, {location['provincia']}...")
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Procesar registros horarios (hourly)
    hourly = response.Hourly()
    hourly_dates = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )
    date_str, time_str = split_datetime(hourly_dates)
    hourly_data = {
        "ubicacion_id": [str(location["_id"])] * len(hourly_dates),
        "date": date_str,
        "time": time_str,
        "data_type": ["hourly"] * len(hourly_dates),
        "temperature": [round(val, 2) for val in hourly.Variables(0).ValuesAsNumpy()],
        "relative_humidity": [round(val, 2) for val in hourly.Variables(1).ValuesAsNumpy()],
        "dew_point": [round(val, 2) for val in hourly.Variables(2).ValuesAsNumpy()],
        "apparent_temperature": [round(val, 2) for val in hourly.Variables(3).ValuesAsNumpy()],
        "precipitation": [round(val, 2) for val in hourly.Variables(4).ValuesAsNumpy()],
        "cloud_cover": [round(val, 0) for val in hourly.Variables(5).ValuesAsNumpy()],
        "wind_speed": [round(val, 2) for val in hourly.Variables(6).ValuesAsNumpy()],
        "wind_gusts": [round(val, 2) for val in hourly.Variables(7).ValuesAsNumpy()],
        "wind_direction": [round(val, 0) for val in hourly.Variables(8).ValuesAsNumpy()],
        "snowfall": [round(val, 2) for val in hourly.Variables(9).ValuesAsNumpy()],
        "pressure": [round(val, 2) for val in hourly.Variables(10).ValuesAsNumpy()]
    }
    hourly_df = pd.DataFrame(hourly_data)
    
    # Procesar registros diarios (daily)
    daily = response.Daily()
    daily_dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )
    date_str_daily, _ = split_datetime(daily_dates)
    daily_data = {
        "ubicacion_id": [str(location["_id"])] * len(daily_dates),
        "date": date_str_daily,
        "data_type": ["daily"] * len(daily_dates),
        "temperature_mean": [round(val, 2) for val in daily.Variables(0).ValuesAsNumpy()],
        "temperature_max": [round(val, 2) for val in daily.Variables(1).ValuesAsNumpy()],
        "temperature_min": [round(val, 2) for val in daily.Variables(2).ValuesAsNumpy()],
        "sunrise": [convert_time_OpenMeteoAPI(ts) for ts in daily.Variables(3).ValuesInt64AsNumpy()],
        "sunset": [convert_time_OpenMeteoAPI(ts) for ts in daily.Variables(4).ValuesInt64AsNumpy()],
        "precipitation_sum": [round(val, 2) for val in daily.Variables(5).ValuesAsNumpy()],
        "snowfall_sum": [round(val, 2) for val in daily.Variables(6).ValuesAsNumpy()],
        "wind_speed_10m_max": [round(val, 2) for val in daily.Variables(7).ValuesAsNumpy()]
    }
    daily_df = pd.DataFrame(daily_data)

    return hourly_df, daily_df

try:
    locations = list(locations_collection.collection.find({}))
    print(f"Se encontraron {len(locations)} ubicaciones.")
except Exception as e:
    print(f"Error al obtener ubicaciones: {e}")
    exit()

# Cargar los registros existentes en cada colección para evitar inserciones duplicadas
existing_hourly = set((doc['ubicacion_id'], doc['date'], doc.get('time', '')) for doc in weather_hourly_collection.collection.find(
        {}, {'ubicacion_id': 1, 'date': 1, 'time': 1, '_id': 0}))

existing_daily = set((doc['ubicacion_id'], doc['date']) for doc in weather_daily_collection.collection.find(
        {}, {'ubicacion_id': 1, 'date': 1, '_id': 0}))

# Procesar cada ubicación e insertar datos en las colecciones correspondientes
for location in locations:
    hourly_df, daily_df = process_location(location)

    # Procesar e insertar registros "hourly"
    hourly_records = hourly_df.to_dict('records')
    new_hourly = []
    for record in hourly_records:
        key = (record['ubicacion_id'], record['date'], record.get('time', ''))
        if key not in existing_hourly:
            new_hourly.append(record)
    if new_hourly:
        weather_hourly_collection.insert_many(new_hourly)
        print(f"Insertados {len(new_hourly)} registros del tipo hourly para {location['municipio']}.")
    else:
        print(f"Sin registros nuevos del tipo hourly para {location['municipio']}.")

    # Procesar e insertar registros "daily"
    daily_records = daily_df.to_dict('records')
    new_daily = []
    for record in daily_records:
        key = (record['ubicacion_id'], record['date'])
        if key not in existing_daily:
            new_daily.append(record)
    if new_daily:
        weather_daily_collection.insert_many(new_daily)
        print(f"Insertados {len(new_daily)} registros del tipo daily para {location['municipio']}.")
    else:
        print(f"Sin registros nuevos del tipo daily para {location['municipio']}.")

    time.sleep(2)  # Pequeña espera 

# Cerrar conexiones
weather_hourly_collection.close_connection()
weather_daily_collection.close_connection()
locations_collection.close_connection()