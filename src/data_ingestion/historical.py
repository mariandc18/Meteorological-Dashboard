import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pymongo import MongoClient
from datetime import datetime
from transformation import convert_time_OpenMeteoAPI, split_datetime


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['weather_db']
weather_collection = db['weather_data']
#weather_collection.delete_many({})
locations_collection = db['locations']

# Make sure all required weather variables are listed here
url = "https://archive-api.open-meteo.com/v1/archive"

def process_location(location):
    params = {
        "latitude": location["location"]["coordinates"][1],
        "longitude": location["location"]["coordinates"][0],
        "start_date": "2025-04-13",
        "end_date": "2025-04-27",
        "daily": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "precipitation_sum", "snowfall_sum", "wind_speed_10m_max"],
        "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "cloud_cover", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m", "snowfall", "pressure_msl", "is_day"]
    }

    print(f"\nProcessing data for {location['municipio']}, {location['provincia']}...")
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

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

    date_str, time_str = split_datetime(hourly_dates)

    # Create hourly data dictionary with location information
    hourly_data = {
        "date": date_str,
        "time": time_str,
        "data_type": ["hourly"] * len(hourly_dates),
        "country": [location["country"]] * len(hourly_dates),
        "provincia": [location["provincia"]] * len(hourly_dates),
        "municipio": [location["municipio"]] * len(hourly_dates),
        #"location": [location["location"]] * len(hourly_dates),
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

    date_str, _ = split_datetime(daily_dates)

    # Create daily data dictionary with location information
    daily_data = {
        "date": date_str,
        "data_type": ["daily"] * len(daily_dates),
        "country": [location["country"]] * len(daily_dates),
        "provincia": [location["provincia"]] * len(daily_dates),
        "municipio": [location["municipio"]] * len(daily_dates),
        #"location": [location["location"]] * len(daily_dates),
        "temperature_mean": daily_temperature_2m_mean,
        "temperature_max": daily_temperature_2m_max,
        "temperature_min": daily_temperature_2m_min,
        "sunrise": [convert_time_OpenMeteoAPI(ts) for ts in daily_sunrise],
        "sunset": [convert_time_OpenMeteoAPI(ts) for ts in daily_sunset],
        "precipitation_sum": daily_precipitation_sum,
        "snowfall_sum": daily_snowfall_sum,
        "wind_speed_10m_max": daily_wind_speed_10m_max   
    }

    daily_dataframe = pd.DataFrame(data = daily_data)
    return pd.concat([hourly_dataframe, daily_dataframe], ignore_index=True)

# Get all locations from MongoDB
locations = list(locations_collection.find({}))
print(f"Found {len(locations)} locations to process")

# Process each location
for location in locations:
    print(f"\nProcessing data for {location['municipio']}, {location['provincia']}...")
    combined_dataframe = process_location(location)
    weather_records = combined_dataframe.to_dict('records')

    # Check for existing records for this location
    existing_hourly = set((doc['date'], doc.get('time', ''), doc['municipio']) 
                        for doc in weather_collection.find(
                            {'data_type': 'hourly', 'municipio': location['municipio']},
                            {'date': 1, 'time': 1, 'municipio': 1, '_id': 0}
                        ))
    
    existing_daily = set((doc['date'], doc['municipio']) 
                       for doc in weather_collection.find(
                           {'data_type': 'daily', 'municipio': location['municipio']},
                           {'date': 1, 'municipio': 1, '_id': 0}
                       ))

    new_records = []
    for record in weather_records:
        if record['data_type'] == 'hourly':
            if (record['date'], record['time'], record['municipio']) not in existing_hourly:
                new_records.append(record)
        else:
            if (record['date'], record['municipio']) not in existing_daily:
                new_records.append(record)

    if new_records:
        print(f"Inserting {len(new_records)} new records for {location['municipio']}...")
        weather_collection.insert_many(new_records)
        print(f"Data successfully inserted for {location['municipio']}!")
    else:
        print(f"No new records to insert for {location['municipio']}. All data already exists in the database.")

print(f"\nDatabase statistics:")
print(f"Total records in database: {weather_collection.count_documents({})}")
print(f"Hourly records: {weather_collection.count_documents({'data_type': 'hourly'})}")
print(f"Daily records: {weather_collection.count_documents({'data_type': 'daily'})}")

client.close() 