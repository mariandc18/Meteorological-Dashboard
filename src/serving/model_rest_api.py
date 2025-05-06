# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from db_manager import MongoDBManager
import pandas as pd
import numpy as np
import joblib
import uvicorn

weather_collection = MongoDBManager(db_name="weather_db", collection_name="weather_data")
app = FastAPI()

model_data = joblib.load('model.pkl')
model = model_data['model']
features = model_data['features']

class InputData(BaseModel):
    date: str
    time: str
    temperature: float
    relative_humidity: float
    dew_point: float
    apparent_temperature: float
    precipitation: float
    cloud_cover: float
    wind_speed: float
    wind_gusts: float
    wind_direction: float
    pressure: float

def preprocess_input(data):
    data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'])
    data = data.sort_values('datetime').reset_index(drop=True)

    data['hour'] = data['datetime'].dt.hour
    data['month'] = data['datetime'].dt.month
    data['dayofweek'] = data['datetime'].dt.dayofweek

    for col, max_val in [('hour', 24), ('month', 12), ('dayofweek', 7)]:
        data[f'{col}_sin'] = np.sin(2 * np.pi * data[col] / max_val)
        data[f'{col}_cos'] = np.cos(2 * np.pi * data[col] / max_val)
    data['temp_humidity'] = data['temperature'] * data['relative_humidity']
    
    return data[features]

@app.post('/predict')
def predict(input_data: InputData):
    # Obtener la fecha y hora actuales
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=48)
    # Consultar los datos de las últimas 48 horas
    recent_data = list(weather_collection.find({
        "datetime": {
            "$gte": start_time,
            "$lte": end_time
        },
        "data_type": "hourly"  
    }))

    if not recent_data:
        return {"error": "No hay suficientes datos para realizar la predicción."}
    
    df = pd.DataFrame(recent_data)
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    processed_data = preprocess_input(df)
    predictions = model.predict(processed_data)
    return {"predictions": predictions.tolist()}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)