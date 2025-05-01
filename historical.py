import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pymongo import MongoClient
from datetime import datetime

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['weather_db']
weather_collection = db['weather_data']

# Make sure all required weather variables are listed here
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 23.133,
    "longitude": -82.383,
    "start_date": "2000-04-13",
    "end_date": "2025-04-27",
    "daily": ["weather_code", "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_mean", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
    "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "rain", "weather_code", "pressure_msl", "surface_pressure", "cloud_cover", "et0_fao_evapotranspiration", "vapour_pressure_deficit", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "soil_temperature_100_to_255cm", "soil_moisture_100_to_255cm"]
}

print("Fetching data from Open-Meteo API...")
responses = openmeteo.weather_api(url, params=params)

# Process first location
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

print("\nProcessing hourly data...")
# Process hourly data
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
hourly_apparent_temperature = hourly.Variables(3).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()
hourly_rain = hourly.Variables(5).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(6).ValuesAsNumpy()
hourly_pressure_msl = hourly.Variables(7).ValuesAsNumpy()
hourly_surface_pressure = hourly.Variables(8).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(9).ValuesAsNumpy()
hourly_et0_fao_evapotranspiration = hourly.Variables(10).ValuesAsNumpy()
hourly_vapour_pressure_deficit = hourly.Variables(11).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(12).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(13).ValuesAsNumpy()
hourly_wind_gusts_10m = hourly.Variables(14).ValuesAsNumpy()
hourly_soil_temperature_100_to_255cm = hourly.Variables(15).ValuesAsNumpy()
hourly_soil_moisture_100_to_255cm = hourly.Variables(16).ValuesAsNumpy()

# Create date range for hourly data
hourly_dates = pd.date_range(
    start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
    end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
    freq = pd.Timedelta(seconds = hourly.Interval()),
    inclusive = "left"
)

# Create hourly data dictionary with separated date and time as strings
hourly_data = {
    "date": [d.strftime('%Y-%m-%d') for d in hourly_dates],
    "time": [d.strftime('%H:%M:%S') for d in hourly_dates],
    "data_type": ["hourly"] * len(hourly_dates),
    "temperature_2m": hourly_temperature_2m,
    "relative_humidity_2m": hourly_relative_humidity_2m,
    "dew_point_2m": hourly_dew_point_2m,
    "apparent_temperature": hourly_apparent_temperature,
    "precipitation": hourly_precipitation,
    "rain": hourly_rain,
    "weather_code": hourly_weather_code,
    "pressure_msl": hourly_pressure_msl,
    "surface_pressure": hourly_surface_pressure,
    "cloud_cover": hourly_cloud_cover,
    "et0_fao_evapotranspiration": hourly_et0_fao_evapotranspiration,
    "vapour_pressure_deficit": hourly_vapour_pressure_deficit,
    "wind_speed_10m": hourly_wind_speed_10m,
    "wind_direction_10m": hourly_wind_direction_10m,
    "wind_gusts_10m": hourly_wind_gusts_10m,
    "soil_temperature_100_to_255cm": hourly_soil_temperature_100_to_255cm,
    "soil_moisture_100_to_255cm": hourly_soil_moisture_100_to_255cm
}

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("Hourly data sample:")
print(hourly_dataframe.head())

print("\nProcessing daily data...")
# Process daily data
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(2).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(3).ValuesAsNumpy()
daily_apparent_temperature_mean = daily.Variables(4).ValuesAsNumpy()
daily_apparent_temperature_max = daily.Variables(5).ValuesAsNumpy()
daily_apparent_temperature_min = daily.Variables(6).ValuesAsNumpy()
daily_sunrise = daily.Variables(7).ValuesInt64AsNumpy()
daily_sunset = daily.Variables(8).ValuesInt64AsNumpy()
daily_daylight_duration = daily.Variables(9).ValuesAsNumpy()
daily_sunshine_duration = daily.Variables(10).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(11).ValuesAsNumpy()
daily_rain_sum = daily.Variables(12).ValuesAsNumpy()
daily_precipitation_hours = daily.Variables(13).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(14).ValuesAsNumpy()
daily_wind_gusts_10m_max = daily.Variables(15).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(16).ValuesAsNumpy()
daily_shortwave_radiation_sum = daily.Variables(17).ValuesAsNumpy()
daily_et0_fao_evapotranspiration = daily.Variables(18).ValuesAsNumpy()

# Create date range for daily data
daily_dates = pd.date_range(
    start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
    end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
    freq = pd.Timedelta(seconds = daily.Interval()),
    inclusive = "left"
)

# Create daily data dictionary with date as string (no time field needed for daily data)
daily_data = {
    "date": [d.strftime('%Y-%m-%d') for d in daily_dates],
    "data_type": ["daily"] * len(daily_dates),
    "weather_code": daily_weather_code,
    "temperature_2m_mean": daily_temperature_2m_mean,
    "temperature_2m_max": daily_temperature_2m_max,
    "temperature_2m_min": daily_temperature_2m_min,
    "apparent_temperature_mean": daily_apparent_temperature_mean,
    "apparent_temperature_max": daily_apparent_temperature_max,
    "apparent_temperature_min": daily_apparent_temperature_min,
    "sunrise": daily_sunrise,
    "sunset": daily_sunset,
    "daylight_duration": daily_daylight_duration,
    "sunshine_duration": daily_sunshine_duration,
    "precipitation_sum": daily_precipitation_sum,
    "rain_sum": daily_rain_sum,
    "precipitation_hours": daily_precipitation_hours,
    "wind_speed_10m_max": daily_wind_speed_10m_max,
    "wind_gusts_10m_max": daily_wind_gusts_10m_max,
    "wind_direction_10m_dominant": daily_wind_direction_10m_dominant,
    "shortwave_radiation_sum": daily_shortwave_radiation_sum,
    "et0_fao_evapotranspiration": daily_et0_fao_evapotranspiration
}

daily_dataframe = pd.DataFrame(data = daily_data)
print("Daily data sample:")
print(daily_dataframe.head())

combined_dataframe = pd.concat([hourly_dataframe, daily_dataframe], ignore_index=True)
weather_records = combined_dataframe.to_dict('records')

print("\nChecking for existing records...")
existing_hourly = set((doc['date'], doc['time']) for doc in weather_collection.find(
    {'data_type': 'hourly'},
    {'date': 1, 'time': 1, '_id': 0}
))
existing_daily = set(doc['date'] for doc in weather_collection.find(
    {'data_type': 'daily'},
    {'date': 1, '_id': 0}
))

new_records = []
for record in weather_records:
    if record['data_type'] == 'hourly':
        if (record['date'], record['time']) not in existing_hourly:
            new_records.append(record)
    else:
        if record['date'] not in existing_daily:
            new_records.append(record)

if new_records:
    print(f"Inserting {len(new_records)} new records...")
    weather_collection.insert_many(new_records)
    print("Data successfully inserted into MongoDB!")
else:
    print("No new records to insert. All data already exists in the database.")

print(f"\nDatabase statistics:")
print(f"Total records in database: {weather_collection.count_documents({})}")
print(f"Hourly records: {weather_collection.count_documents({'data_type': 'hourly'})}")
print(f"Daily records: {weather_collection.count_documents({'data_type': 'daily'})}")

client.close() 