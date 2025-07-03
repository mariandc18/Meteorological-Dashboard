from dash import Input, Output
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from src.storage.tables import UserInteraction
from datetime import datetime
import uuid
from pages.tracking import log_interaction_by_username
from pages.db import get_db_session

def register_callbacks(app):
    @app.callback(
        Output("provincia", "options"),
        Input("url", "pathname"),
        Input("user-session", "data") 
    )
    def update_provincia_options(pathname, user_data):
        if pathname != "/historical_analysis":
            return []

        session = get_db_session()
        provs = session.execute(text("SELECT DISTINCT province FROM locations")).fetchall()
        session.close()

        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "historical", "provincia_dropdown", "ver opciones")

        return [{"label": p[0], "value": p[0]} for p in sorted(provs)]

    @app.callback(
        Output("municipio", "options"),
        Input("provincia", "value"),
        Input("user-session", "data")
    )
    def update_municipio_options(selected, user_data):
        if not selected:
            return []

        session = get_db_session()
        mun = session.execute(
            text("SELECT DISTINCT municipality FROM locations WHERE province = :province"),
            {"province": selected}
        ).fetchall()
        session.close()

        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "historical", "municipio_dropdown", selected)

        return [{"label": m[0], "value": m[0]} for m in sorted(mun)]

    @app.callback(
        Output("variable", "options"),
        Input("data-type", "value"),
        Input("user-session", "data")
    )
    def update_variable_options(data_type, user_data):
        WeatherTable = "weather_hourly" if data_type == "hourly" else "weather_daily"

        session = get_db_session()
        columns = session.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = :table"),
            {"table": WeatherTable}
        ).fetchall()
        session.close()

        exclude_columns = {"ubicacion_id", "date", "time"}

        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "historical", "variable_dropdown", data_type)

        return [{"label": col[0], "value": col[0]} for col in columns if col[0] not in exclude_columns]

    @app.callback(
        Output("weather-graph", "figure"),
        [
            Input("data-type", "value"),
            Input("provincia", "value"),
            Input("municipio", "value"),
            Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
            Input("agregacion", "value"),
            Input("variable", "value"),
            Input("user-session", "data")  
        ]
    )
    def update_graph(data_type, prov, mun, start, end, agg, var, user_data):
        WeatherTable = "weather_hourly" if data_type == "hourly" else "weather_daily"

        if not prov or not mun:
            return px.scatter(title="Debe seleccionar una provincia y un municipio")

        if not var:
            var = "temperature" if data_type == "hourly" else "temperature_mean"

        session = get_db_session()
        ids = session.execute(
            text("SELECT id FROM locations WHERE province = :province AND municipality = :municipality"),
            {"province": prov, "municipality": mun}
        ).fetchall()
        session.close()

        ids = tuple(str(d[0]) for d in ids)

        if not ids:
            return px.scatter(title="No hay ubicaciones para ese filtro")

        session = get_db_session()
        query = text(f"SELECT date, {var} FROM {WeatherTable} WHERE ubicacion_id::TEXT IN :ids AND date >= :start AND date <= :end")
        params = {"ids": ids, "start": start, "end": end}

        results = session.execute(query, params).fetchall()
        session.close()

        if not results:
            return px.scatter(title="Sin datos en el rango de fechas")

        df = pd.DataFrame(results, columns=["date", var])
        df["date"] = pd.to_datetime(df["date"])
        df["period"] = df["date"].dt.to_period(agg[0].upper()).astype(str)
        grp = df.groupby("period")[var].mean().reset_index()

        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "historical", "weather_graph", f"Datos desde {start} hasta {end}")

        fig = px.line(grp, x="period", y=var, title=f"{var.replace('_', ' ').title()} promedio por {agg.title()}")
        fig.update_layout(xaxis_title="Periodo", yaxis_title=var)
        return fig