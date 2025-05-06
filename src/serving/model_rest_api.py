from fastapi import FastAPI
import pandas as pd
import numpy as np
import joblib
from pydantic import BaseModel
from typing import Optional


def load_model(path='model_new.pkl'):
    model_data = joblib.load(path)
    return model_data['model'], model_data['features']

model, features = load_model()
app = FastAPI()

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
    ubicacion_id: Optional[str] = None

def preprocess_input(data: pd.DataFrame) -> pd.DataFrame:
    
    if 'datetime' not in data.columns or data['datetime'].dtype == object:
        data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'], errors='coerce')
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
def predict(user_data: Optional[list[InputData]] = None):
    if not user_data:
        return {"error": "No se han enviado datos para la predicción."}
    
    df = pd.DataFrame([data.dict() for data in user_data])
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], errors='coerce')
    
    if df['datetime'].isnull().all():
        return {"error": "No se pudieron convertir los campos 'date' y 'time' correctamente."}

    processed_data = preprocess_input(df)
    predictions = model.predict(processed_data)

    return {"predictions": predictions.tolist()}