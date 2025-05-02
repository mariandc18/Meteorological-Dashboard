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
    "daily": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "precipitation_sum", "snowfall_sum", "wind_speed_10m_max"],
	"hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "cloud_cover", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m", "snowfall", "pressure_msl", "is_day"]
}

print("Fetching data from Open-Meteo API...")
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
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
hourly_cloud_cover = hourly.Variables(5).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(6).ValuesAsNumpy()
hourly_wind_gusts_10m = hourly.Variables(7).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(8).ValuesAsNumpy()
hourly_snowfall = hourly.Variables(9).ValuesAsNumpy()
hourly_pressure_msl = hourly.Variables(10).ValuesAsNumpy()
hourly_is_day = hourly.Variables(11).ValuesAsNumpy()

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
    "temperature": hourly_temperature_2m,
    "relative_humidity": hourly_relative_humidity_2m,
    "dew_point": hourly_dew_point_2m,
    "apparent_temperature": hourly_apparent_temperature,
    "precipitation": hourly_precipitation,
    "pressure": hourly_pressure_msl,
    "cloud_cover": hourly_cloud_cover,
    "wind_speed": hourly_wind_speed_10m,
    "wind_direction": hourly_wind_direction_10m,
    "wind_gusts": hourly_wind_gusts_10m
}

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("Hourly data sample:")
print(hourly_dataframe.head())

print("\nProcessing daily data...")
# Process daily data
daily = response.Daily()
daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
daily_sunrise = daily.Variables(3).ValuesInt64AsNumpy()
daily_sunset = daily.Variables(4).ValuesInt64AsNumpy()
daily_precipitation_sum = daily.Variables(5).ValuesAsNumpy()
daily_snowfall_sum = daily.Variables(6).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(7).ValuesAsNumpy()

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
    "temperature_mean": daily_temperature_2m_mean,
    "temperature_max": daily_temperature_2m_max,
    "temperature_min": daily_temperature_2m_min,
    "sunrise": daily_sunrise,
    "sunset": daily_sunset,
    "precipitation_sum": daily_precipitation_sum,
    "snowfall_sum": daily_snowfall_sum,
    "wind_speed_10m_max": daily_wind_speed_10m_max   
}

daily_dataframe = pd.DataFrame(data = daily_data)
print("Daily data sample:")
print(daily_dataframe.head())

combined_dataframe = pd.concat([hourly_dataframe, daily_dataframe], ignore_index=True)
weather_records = combined_dataframe.to_dict('records')

print("\nChecking for existing records...")
existing_hourly = set((doc['date'], doc.get('time', '')) for doc in weather_collection.find(
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