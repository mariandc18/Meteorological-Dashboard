from dash import Input, Output, html,dcc
import pandas as pd
from pages.db import locations_collection, weather_hourly_collection
import requests
from datetime import datetime, timedelta
import plotly.express as px

API_FORECAST_URL = "http://127.0.0.1:8000/predict"

def register_callbacks(app):
    @app.callback(
        Output("forecast-provincia", "options"),
        Input("url", "pathname")
    )
    def update_forecast_provincia_options(pathname):
        if pathname != "/forecast":
            return []
        df = pd.DataFrame(list(locations_collection.collection.find({})))
        df["provincia"] = df["provincia"].astype(str).str.strip()
        provs = sorted(df["provincia"].unique())
        return [{"label": prov, "value": prov} for prov in provs]

    @app.callback(
        Output("forecast-municipio", "options"),
        Input("forecast-provincia", "value")
    )
    def update_forecast_municipio_options(selected_provincia):
        if not selected_provincia:
            return []
        df = pd.DataFrame(list(locations_collection.collection.find({})))
        df["provincia"] = df["provincia"].astype(str).str.strip()
        df["municipio"] = df["municipio"].astype(str).str.strip()
        mun = sorted(df[df["provincia"] == selected_provincia]["municipio"].unique())
        return [{"label": m, "value": m} for m in mun]
    
    @app.callback(
    Output("forecast-graphs", "children"),
    [Input("forecast-provincia", "value"),
     Input("forecast-municipio", "value")]
)
    def update_forecast_graphs(provincia, municipio):
        if not provincia or not municipio:
            return html.P("Selecciona provincia y municipio para ver el pronóstico.")

        df_loc = pd.DataFrame(list(locations_collection.collection.find({
            "provincia": provincia,
            "municipio": municipio
        })))
        
        if df_loc.empty:
            return html.P("No se encontró la ubicación seleccionada en la base de datos.")
        
        ubicacion_id = str(df_loc.iloc[0].get("ubicacion_id", df_loc.iloc[0]["_id"]))
        print("Ubicación seleccionada:", ubicacion_id)

        try:
            df_last = pd.DataFrame(list(weather_hourly_collection.collection.find({"ubicacion_id": ubicacion_id})))
            df_last = df_last.drop(columns= ["snowfall", "is_day"])
            if df_last.empty:
                return html.P("No se encontraron datos de clima para la ubicación seleccionada.")
            
            if "datetime" not in df_last.columns or df_last["datetime"].dtype == object:
                df_last["datetime"] = pd.to_datetime(df_last["date"] + " " + df_last["time"], errors='coerce')
            df_last = df_last.sort_values("datetime")
            
            latest_record = df_last.iloc[-48]
            print("Total de registros en latest_records:", latest_record.shape[0])

        except Exception as e:
            return html.P(f"Error al recuperar datos de clima: {e}")
        
        payload = latest_record.to_frame().T.to_dict(orient="records") 
        for rec in payload:
            rec.pop("datetime", None)
            if "ubicacion_id" in rec:
                rec["ubicacion_id"] = str(rec["ubicacion_id"])
            if "_id" in rec: 
                rec["_id"] = str(rec["_id"])
        print(payload)

        try:
            response = requests.post(API_FORECAST_URL, json=payload, proxies={"http": None, "https": None})
            response.raise_for_status()
        except requests.exceptions.HTTPError as he:
            try:
                err = response.json().get("detail", response.text)
            except:
                err = response.text
            return html.Pre(f"Error {response.status_code} al obtener pronóstico:\n{err}")
        except Exception as e:
            return html.Pre(f"Error al conectar con la API:\n{e}")
        
        pred_data = response.json()
        predictions = pred_data.get("predictions", [])
        if not predictions:
            return html.P("No hay datos de pronóstico para la ubicación seleccionada.")
        
        
        forecast_features = [
            "temperature", "relative_humidity", "dew_point", "apparent_temperature",
            "precipitation", "cloud_cover", "wind_speed", "wind_gusts",
            "wind_direction", "pressure"
        ]
        n_hours = len(predictions)
        
        try:
            last_time = latest_record["datetime"].iloc[0]
        except Exception:
            last_time = datetime.now()
        
        forecast_times = [(last_time + timedelta(hours=i + 1)).strftime("%H:%M") for i in range(n_hours)]
        graphs = []
        for idx, feature in enumerate(forecast_features):
            feature_values = [pred[idx] for pred in predictions]
            df_forecast = pd.DataFrame({
                "Hora": forecast_times,
                feature: feature_values
            })
            fig = px.line(df_forecast, x="Hora", y=feature, title=f"Evolución de {feature}")
            fig.update_layout(xaxis_title="Hora", yaxis_title=feature)
            graphs.append(dcc.Graph(figure=fig))
        
        return graphs