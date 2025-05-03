import requests
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from transformation import convert_time_WheatherAPI, split_datetime
import time

client = MongoClient('mongodb://localhost:27017/')
db = client['weather_db']
weather_collection = db['weather_data']
locations_collection = db['locations']

# WeatherAPI configuration
API_KEY = "API Key"
HISTORY_URL = "https://api.weatherapi.com/v1/history.json"

def fetch_hourly_data(location):
    current_time = datetime.now(timezone.utc)
    current_hour = current_time.hour
    today = current_time.strftime("%Y-%m-%d")
    
    print(f"\nFetching data for {location['municipio']}, {location['provincia']} - {today}")
    print(f"Current time (UTC): {current_time.strftime('%H:%M')}")
    
    coords = f"{location['location']['coordinates'][1]},{location['location']['coordinates'][0]}"
    params = {"key": API_KEY, "q": coords, "dt": today}
    
    resp = requests.get(HISTORY_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Filtrar horas hasta la hora actual
    hours = data["forecast"]["forecastday"][0]["hour"]
    target_hours = [h for h in hours if datetime.fromtimestamp(h["time_epoch"], tz=timezone.utc).hour <= current_hour]
    
    if target_hours:
        first_hour = datetime.fromtimestamp(target_hours[0]["time_epoch"], tz=timezone.utc)
        last_hour = datetime.fromtimestamp(target_hours[-1]["time_epoch"], tz=timezone.utc)
        print(f"Data range: from {first_hour.strftime('%H:%M')} to {last_hour.strftime('%H:%M')} UTC")

    # Preparar los datos para Mongo
    records = []
    for h in target_hours:
        dt = datetime.fromtimestamp(h["time_epoch"], tz=timezone.utc)
        date, time = split_datetime(dt)
        rec = {
            "date": date,
            "time": time,
            "data_type": "hourly",
            "country": location["country"],
            "provincia": location["provincia"],
            "municipio": location["municipio"],
            #"location": location["location"],
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

    existing_records = set(
        (d.get("date", ""), d.get("time", ""), d.get("municipio", "")) 
        for d in weather_collection.find(
            {"data_type": "hourly", "date": today, "municipio": location["municipio"]}, 
            {"date": 1, "time": 1, "municipio": 1, "_id": 0}
        )
    )
    
    new_records = [r for r in records if (r["date"], r["time"], r["municipio"]) not in existing_records]

    if new_records:
        weather_collection.insert_many(new_records)
        print(f"Inserted {len(new_records)} new records for {location['municipio']}.")
        print(f"First record: {new_records[0]['date']} {new_records[0]['time']}")
        print(f"Last record: {new_records[-1]['date']} {new_records[-1]['time']}")
    else:
        print(f"No new records to insert for {location['municipio']}.")

def fetch_and_update_daily(location):
    yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
    date, _ = split_datetime(datetime.combine(yesterday, datetime.min.time()))

    # Comprobar si ya existe daily
    existing_doc = weather_collection.find_one({
        "date": date,
        "data_type": "daily",
        "municipio": location["municipio"]
    })

    coords = f"{location['location']['coordinates'][1]},{location['location']['coordinates'][0]}"
    params = {"key": API_KEY, "q": coords, "dt": yesterday.strftime("%Y-%m-%d")}
    
    resp = requests.get(HISTORY_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    day = data["forecast"]["forecastday"][0]["day"]

    # Construir documento daily
    daily_doc = {
        "date": date,
        "data_type": "daily",
        "country": location["country"],
        "provincia": location["provincia"],
        "municipio": location["municipio"],
        #"location": location["location"],
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
        print(f"Verificando cambios en registro daily para {location['municipio']} - {date}...")
        changes = {}
        for key, value in daily_doc.items():
            if key not in ("date", "data_type", "country", "provincia", "municipio", "location") and existing_doc.get(key) != value:
                changes[key] = value
        
        if changes:
            weather_collection.update_one(
                {"_id": existing_doc["_id"]},
                {"$set": changes}
            )
            print(f"Documento daily para {location['municipio'], location['provincia'], location['country'], date} actualizado con campos: {', '.join(changes.keys())}.")
        else:
            print(f"Documento daily para {location['municipio'], location['provincia'], location['country'], date} ya está actualizado, no hay cambios.")
    else:
        weather_collection.insert_one(daily_doc)
        print(f"Documento daily para {location['municipio'], location['provincia'], location['country'], date} insertado.")

if __name__ == "__main__":
    locations = list(locations_collection.find({}))
    print(f"Found {len(locations)} locations to process")
    
    for location in locations:
        print(f"\nProcessing {location['municipio']}, {location['provincia']}...")
        fetch_hourly_data(location)
        time.sleep(5)
        fetch_and_update_daily(location)
        time.sleep(5)
    
    client.close()