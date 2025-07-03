from dash import Input, Output, html, dcc
import pandas as pd
import plotly.express as px
import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from pages.db import engine
from pages.tracking import log_interaction_by_username

API_FORECAST_URL = "http://127.0.0.1:8000/predict"

Session = sessionmaker(bind=engine)
def register_callbacks(app):
    @app.callback(
        Output("forecast-provincia", "options"),
        [Input("url", "pathname"), Input("user-session", "data")]
    )
    def update_forecast_provincia_options(pathname, user_data):
        if pathname != "/forecast":
            return []

        session = Session()
        provs = session.execute(text("SELECT DISTINCT province FROM locations")).fetchall()
        session.close()
        
        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "forecast", "forecast-provincia", "ver opciones")

        return [{"label": p[0], "value": p[0]} for p in sorted(provs)]

    @app.callback(
        Output("forecast-municipio", "options"),
        [Input("forecast-provincia", "value"), Input("user-session", "data")]
    )
    def update_forecast_municipio_options(selected_provincia, user_data):
        if not selected_provincia:
            return []

        session = Session()
        mun = session.execute(
            text("SELECT DISTINCT municipality FROM locations WHERE province = :province"),
            {"province": selected_provincia}
        ).fetchall()
        session.close()

        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "forecast", "forecast-municipio", selected_provincia)

        return [{"label": m[0], "value": m[0]} for m in sorted(mun)]

    @app.callback(
        Output("forecast-graphs", "children"),
        [Input("forecast-provincia", "value"),
         Input("forecast-municipio", "value"),
         Input("user-session", "data")]
    )
    def update_forecast_graphs(provincia, municipio, user_data):
        if not provincia or not municipio:
            return html.P("Selecciona provincia y municipio para ver el pronóstico.")

        session = Session()
        ubicacion_id = session.execute(
            text("SELECT id FROM locations WHERE province = :province AND municipality = :municipality"),
            {"province": provincia, "municipality": municipio}
        ).fetchone()
        session.close()

        if not ubicacion_id:
            return html.P("No se encontró la ubicación en la base de datos.")

        ubicacion_id = str(ubicacion_id[0])

        session = Session()
        latest_record = session.execute(
            text("SELECT * FROM weather_hourly WHERE ubicacion_id = :id ORDER BY date DESC LIMIT 48"),
            {"id": ubicacion_id}
        ).fetchall()
        session.close()

        if not latest_record:
            return html.P("No se encontraron datos de clima recientes.")

        payload = [dict(row._mapping) for row in latest_record]
        for rec in payload:
            rec.pop("id", None)

        try:
            response = requests.post(API_FORECAST_URL, json=payload)
            response.raise_for_status()
            pred_data = response.json()
        except requests.exceptions.RequestException as e:
            return html.Pre(f"Error al obtener pronóstico:\n{e}")

        forecast_features = ["temperature", "relative_humidity", "wind_speed"]
        forecast_times = [(datetime.now() + timedelta(hours=i + 1)).strftime("%H:%M") for i in range(len(pred_data["predictions"]))]

        graphs = [
            dcc.Graph(
                figure=px.line(
                    pd.DataFrame({"Hora": forecast_times, f: [p[i] for p in pred_data["predictions"]]}),
                    x="Hora", y=f, title=f"Evolución de {f}"
                )
            ) for i, f in enumerate(forecast_features)
        ]

        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "forecast", "forecast-graphs", f"Generó gráficos para {provincia}, {municipio}")

        return graphs