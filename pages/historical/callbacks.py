from dash import Input, Output
import pandas as pd
import plotly.express as px
from pages.db import locations_collection, weather_hourly_collection, weather_daily_collection


def register_callbacks(app):
    @app.callback(
        Output("provincia", "options"),
        Input("url", "pathname")
    )
    def update_provincia_options(pathname):
        if pathname != "/historical_analysis":
            return []
        df = pd.DataFrame(list(locations_collection.collection.find({})))
        df["provincia"] = df["provincia"].astype(str).str.strip()
        provs = sorted(df["provincia"].unique())
        return [{"label": prov, "value": prov} for prov in provs]

    @app.callback(
        Output("municipio", "options"),
        Input("provincia", "value")
    )
    def update_municipio_options(selected):
        df = pd.DataFrame(list(locations_collection.collection.find({})))
        df["provincia"] = df["provincia"].astype(str).str.strip()
        df["municipio"] = df["municipio"].astype(str).str.strip()
        if not selected:
            return []
        mun = sorted(df[df["provincia"] == selected]["municipio"].unique())
        return [{"label": m, "value": m} for m in mun]

    @app.callback(
        Output("variable", "options"),
        Input("data-type", "value")
    )
    def update_variable_options(data_type):
        if data_type == "hourly":
            vals = [
                "temperature", "relative_humidity", "dew_point", "apparent_temperature",
                "precipitation", "cloud_cover", "wind_speed", "wind_gusts", "wind_direction",
                "snowfall", "pressure"
            ]
        else:
            vals = [
                "temperature_mean", "temperature_max", "temperature_min",
                "sunrise", "sunset", "precipitation_sum", "snowfall_sum", "wind_speed_10m_max"
            ]
        return [{"label": v.replace("_", " ").title(), "value": v} for v in vals]

    @app.callback(
        Output("weather-graph", "figure"),
        [
            Input("data-type", "value"),
            Input("provincia", "value"),
            Input("municipio", "value"),
            Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("agregacion", "value"),
            Input("variable", "value")
        ]
    )
    def update_graph(data_type, prov, mun, start, end, agg, var):
        if not var:
            var = "temperature" if data_type == "hourly" else "temperature_mean"
        
        # Filtrar ubicaciones según los datos seleccionados
        filt = {}
        if prov:
            filt["provincia"] = prov
        if mun:
            filt["municipio"] = mun
        locs = list(locations_collection.collection.find(filt))
        ids = [str(d["_id"]) for d in locs]
        if not ids:
            return px.scatter(title="No hay ubicaciones para ese filtro")
        
        coll = weather_hourly_collection if data_type == "hourly" else weather_daily_collection
        df = pd.DataFrame(list(coll.collection.find({"ubicacion_id": {"$in": ids}})))
        if df.empty:
            return px.scatter(title="Sin datos para esos filtros")
        df["date"] = pd.to_datetime(df["date"])
        if start:
            df = df[df["date"] >= start]
        if end:
            df = df[df["date"] <= end]
        if df.empty:
            return px.scatter(title="Sin datos en el rango de fechas")
        
        if agg == "day":
            df["period"] = df["date"].dt.to_period("D").astype(str)
        elif agg == "month":
            df["period"] = df["date"].dt.to_period("M").astype(str)
        elif agg == "year":
            df["period"] = df["date"].dt.year.astype(str)
        
        grp = df.groupby("period")[var].mean().reset_index()
        
        if agg == "day":
            period_label = "Día"
        elif agg == "month":
            period_label = "Mes"
        else:
            period_label = "Año"
        
        fig = px.line(grp, x="period", y=var, title=f"{var.replace('_', ' ').title()} promedio por {period_label}")
        fig.update_layout(xaxis_title="Periodo", yaxis_title=var)
        return fig