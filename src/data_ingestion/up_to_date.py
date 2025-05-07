import requests
from datetime import datetime, timezone, timedelta
from src.storage.db_manager import MongoDBManager
from src.transformation.transformation import convert_time_WheatherAPI, split_datetime
import time
import pytz 

# Conexión a Mongo
locations_collection = MongoDBManager(db_name="weather_db", collection_name="locations")
weather_hourly_collection = MongoDBManager(db_name="weather_db", collection_name="weather_hourly")
weather_daily_collection = MongoDBManager(db_name="weather_db", collection_name="weather_daily")

# Configuración de WeatherAPI
API_KEY = "Api Key"
HISTORY_URL = "https://api.weatherapi.com/v1/history.json"
CUBA_TZ = pytz.timezone("America/Havana") 

def fetch_hourly_data(location):
    current_time = datetime.now(CUBA_TZ)  # Usar zona horaria de Cuba
    current_hour = current_time.hour
    today = current_time.strftime("%Y-%m-%d")
    
    print(f"\nFetching data for ubicacion_id {str(location['municipio'])} - {today}")
    print(f"Current time (Cuba): {current_time.strftime('%H:%M')}")
    
    coords = f"{location['location']['coordinates'][1]},{location['location']['coordinates'][0]}"
    params = {"key": API_KEY, "q": coords, "dt": today}
    
    resp = requests.get(HISTORY_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    
    # Convertir cada registro a la zona horaria de Cuba
    hours = data["forecast"]["forecastday"][0]["hour"]
    target_hours = [
    h for h in hours if datetime.fromtimestamp(int(h["time_epoch"]), timezone.utc).astimezone(CUBA_TZ).hour <= current_hour
]
    
    if target_hours:
        first_hour = datetime.fromtimestamp(target_hours[0]["time_epoch"], tz=timezone.utc).astimezone(CUBA_TZ)
        last_hour = datetime.fromtimestamp(target_hours[-1]["time_epoch"], tz=timezone.utc).astimezone(CUBA_TZ)
        print(f"Data range (Cuba): from {first_hour.strftime('%H:%M')} to {last_hour.strftime('%H:%M')}")
    
    records = []
    for h in target_hours:
        dt = datetime.fromtimestamp(h["time_epoch"], tz=timezone.utc).astimezone(CUBA_TZ)
        date_str, time_str = split_datetime(dt)
        rec = {
            "date": date_str,
            "time": time_str,
            "data_type": "hourly",
            "ubicacion_id": str(location["_id"]),
            "temperature": h.get("temp_c"),
            "relative_humidity": h.get("humidity"),
            "dew_point": h.get("dewpoint_c"),
            "apparent_temperature": h.get("feelslike_c"),
            "precipitation": h.get("precip_mm"),
            "pressure": h.get("pressure_mb"),
            "cloud_cover": h.get("cloud"),
            "wind_speed": h.get("wind_kph"),
            "wind_direction": h.get("wind_degree"),
            "wind_gusts": h.get("gust_kph"),
            "is_day": h.get("is_day")
        }
        records.append(rec)
    
    # Evitar duplicados: se obtienen registros existentes para el día actual y la ubicación, usando "ubicacion_id"
    existing_records = set(
        (d.get("date", ""), d.get("time", ""), d.get("ubicacion_id", ""))
        for d in weather_hourly_collection.collection.find(
            {"date": today, "data_type": "hourly", "ubicacion_id": str(location["_id"])},
            {"date": 1, "time": 1, "ubicacion_id": 1, "_id": 0}
        )
    )
    
    new_records = [r for r in records if (r["date"], r["time"], r["ubicacion_id"]) not in existing_records]
    
    if new_records:
        weather_hourly_collection.insert_many(new_records)
        print(f"Inserted {len(new_records)} new hourly records for ubicacion_id {str(location['_id'])}.")
        print(f"First record: {new_records[0]['date']} {new_records[0]['time']}")
        print(f"Last record: {new_records[-1]['date']} {new_records[-1]['time']}")
    else:
        print(f"No new hourly records to insert for ubicacion_id {str(location['_id'])}.")

def fetch_and_update_daily(location):
    yesterday_date = datetime.now(timezone.utc).date() - timedelta(days=1)
    yesterday_datetime = datetime.combine(yesterday_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    date_str, _ = split_datetime(yesterday_datetime)
    
    # Buscar si ya existe el documento daily en la colección correspondiente usando "ubicacion_id"
    existing_doc = weather_daily_collection.collection.find_one({
        "date": date_str,
        "data_type": "daily",
        "ubicacion_id": str(location["_id"])
    })
    
    coords = f"{location['location']['coordinates'][1]},{location['location']['coordinates'][0]}"
    params = {"key": API_KEY, "q": coords, "dt": yesterday_date.strftime("%Y-%m-%d")}
    
    resp = requests.get(HISTORY_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    day = data["forecast"]["forecastday"][0]["day"]
    
    daily_doc = {
        "date": date_str,
        "data_type": "daily",
        "ubicacion_id": str(location["_id"]),
        "temperature_mean": day.get("avgtemp_c"),
        "temperature_max": day.get("maxtemp_c"),
        "temperature_min": day.get("mintemp_c"),
        "sunrise": convert_time_WheatherAPI(data["forecast"]["forecastday"][0]["astro"].get("sunrise")),
        "sunset": convert_time_WheatherAPI(data["forecast"]["forecastday"][0]["astro"].get("sunset")),
        "precipitation_sum": day.get("totalprecip_mm"),
        "snowfall_sum": day.get("totalsnow_cm"),
        "wind_speed_10m_max": day.get("maxwind_kph")
    }
    
    if existing_doc:
        print(f"Checking changes in daily record for ubicacion_id {str(location['municipio'])} - {date_str}...")
        changes = {}
        for key, value in daily_doc.items():
            if key not in ("date", "data_type", "ubicacion_id") and existing_doc.get(key) != value:
                changes[key] = value
        if changes:
            weather_daily_collection.collection.update_one(
                {"_id": existing_doc["_id"]},
                {"$set": changes}
            )
            print(f"Updated daily document for ubicacion_id {str(location['municipio'])} - {date_str} with fields: {', '.join(changes.keys())}.")
        else:
            print(f"Daily document for ubicacion_id {str(location['municipio'])} - {date_str} is already up-to-date.")
    else:
        weather_daily_collection.collection.insert_one(daily_doc)
        print(f"Inserted daily document for ubicacion_id {str(location['municipio'])} - {date_str}.")

if __name__ == "__main__":
    locations = list(locations_collection.collection.find({}))
    print(f"Found {len(locations)} locations to process")
    
    for location in locations:
        print(f"\nProcessing ubicacion_id {str(location['municipio'])}...")
        fetch_hourly_data(location)
        time.sleep(5)
        fetch_and_update_daily(location)
        time.sleep(5)
    
    locations_collection.close_connection()
    weather_hourly_collection.close_connection()
    weather_daily_collection.close_connection()