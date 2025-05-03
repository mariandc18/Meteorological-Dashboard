import requests
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from transformation import convert_time_WheatherAPI, split_datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['weather_db']
weather_collection = db['weather_data']
#weather_collection.delete_many({})

# WeatherAPI configuration
API_KEY = "API Key"
LOCATION = "40.4168,-3.7038"
HISTORY_URL = "https://api.weatherapi.com/v1/history.json"

def fetch_hourly_data():
    try:
        current_time = datetime.now(timezone.utc)
        current_hour = current_time.hour
        today = current_time.strftime("%Y-%m-%d")
        
        print(f"\nFetching data for date: {today}")
        print(f"Current time (UTC): {current_time.strftime('%H:%M')}")
        
        params = {"key": API_KEY, "q": LOCATION, "dt": today}
        resp = requests.get(HISTORY_URL, params=params)
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
            (d.get("date", ""), d.get("time", "")) 
            for d in weather_collection.find(
                {"data_type": "hourly", "date": today}, 
                {"date": 1, "time": 1, "_id": 0}
            )
        )
        
        new_records = [r for r in records if (r["date"], r["time"]) not in existing_records]

        if new_records:
            weather_collection.insert_many(new_records)
            print(f"Inserted {len(new_records)} new records.")
            print(f"First record: {new_records[0]['date']} {new_records[0]['time']}")
            print(f"Last record: {new_records[-1]['date']} {new_records[-1]['time']}")
        else:
            print("No new records to insert.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def fetch_and_update_daily():
    yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
    date, _ = split_datetime(datetime.combine(yesterday, datetime.min.time()))

    # Comprobar si ya existe daily
    existing_doc = weather_collection.find_one({
        "date": date,
        "data_type": "daily"
    })

    if existing_doc:
        print(f"Ya existe un registro daily para {date}. Verificando si hay cambios...")
        # Obtener datos nuevos
        params = {"key": API_KEY, "q": LOCATION, "dt": yesterday.strftime("%Y-%m-%d")}
        resp = requests.get(HISTORY_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        day = data["forecast"]["forecastday"][0]["day"]

        # Construir documento daily
        daily_doc = {
            "date": date,
            "data_type": "daily",
            "temperature_mean": day.get("avgtemp_c"),
            "temperature_max": day.get("maxtemp_c"),
            "temperature_min": day.get("mintemp_c"),
            "sunrise": convert_time_WheatherAPI(data["forecast"]["forecastday"][0]["astro"].get("sunrise")),
            "sunset": convert_time_WheatherAPI(data["forecast"]["forecastday"][0]["astro"].get("sunset")),
            "precipitation_sum": day.get("totalprecip_mm"),
            "snowfall_sum": day.get("totalsnow_cm"),
            "wind_speed_10m_max": day.get("maxwind_kph")
        }

        changes = {}
        for key, value in daily_doc.items():
            if key not in ("date", "data_type") and existing_doc.get(key) != value:
                changes[key] = value
        
        if changes:
            # Solo se actualiza si hay cambios
            weather_collection.update_one(
                {"_id": existing_doc["_id"]},
                {"$set": changes}
            )
            print(f"Documento daily para {date} actualizado con campos: {', '.join(changes.keys())}.")
        else:
            print(f"Documento daily para {date} ya está actualizado, no hay cambios.")
    else:
        # Si no existe, obtener e insertar nuevos datos
        params = {"key": API_KEY, "q": LOCATION, "dt": yesterday.strftime("%Y-%m-%d")}
        resp = requests.get(HISTORY_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        day = data["forecast"]["forecastday"][0]["day"]

        daily_doc = {
            "date": date,
            "data_type": "daily",
            "temperature_mean": day.get("avgtemp_c"),
            "temperature_max": day.get("maxtemp_c"),
            "temperature_min": day.get("mintemp_c"),
            "sunrise": convert_time_WheatherAPI(data["forecast"]["forecastday"][0]["astro"].get("sunrise")),
            "sunset": convert_time_WheatherAPI(data["forecast"]["forecastday"][0]["astro"].get("sunset")),
            "precipitation_sum": day.get("totalprecip_mm"),
            "snowfall_sum": day.get("totalsnow_cm"),
            "wind_speed_10m_max": day.get("maxwind_kph")
        }

        weather_collection.insert_one(daily_doc)
        print(f"Documento daily para {date} insertado.")

if __name__ == "__main__":
    fetch_hourly_data()
    fetch_and_update_daily()
    client.close()