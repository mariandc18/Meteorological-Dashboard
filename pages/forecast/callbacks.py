from dash import Input, Output, html
import pandas as pd
from pages.db import locations_collection, weather_hourly_collection

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