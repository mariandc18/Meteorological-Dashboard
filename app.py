import dash
from dash import dcc, html, Input, Output
import pandas as pd
import requests
from src.storage.db_manager import MongoDBManager
from pages.forecast.layout import forecast_layout
from pages.historical.layout import historical_analysis_layout
from pages.forecast.callbacks import register_callbacks as register_forecast_callbacks
from pages.historical.callbacks import register_callbacks as register_historical_callbacks
from pages.db import locations_collection, weather_hourly_collection, weather_daily_collection
#from src.serving import model_rest_api

# URL del endpoint de Rest API
API_FORECAST_URL = "http://127.0.0.1:8000/predict"

# Creación de la app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Weather Dashboard"

# Layout principal
app.layout = html.Div([
    html.Div([
        html.H2("Menú principal"),
        dcc.Link("Análisis histórico del clima 📈", href="/historical_analysis"),
        html.Br(),
        dcc.Link("Pronóstico del tiempo ⛅", href="/forecast"),
    ], className="sidebar"),

    html.Div([
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ], className="content")
])

default_layout = html.Div([
    html.H1("Análisis y predicción del clima de Cuba"),
    html.P("Este dashboard ofrece información sobre la evolución del clima por más de 30 años. Tiene en cuenta varias variables meteorológicas, desde temperatura, viento, humedad, precipitaciones, rocío, entre otras."),
    html.P("Puede analizar registros históricos o consultar el pronóstico del clima para las próximas horas."),
    html.Img(src="/assets/clima.png", style={"width": "85%", "display": "block", "margin": "auto"})
])

# Callback para manejar navegación entre páginas
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/forecast":
        return forecast_layout
    elif pathname == "/historical_analysis":
        return historical_analysis_layout
    return default_layout

# Registrar callbacks en la app
register_forecast_callbacks(app)
register_historical_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
