from dash import Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy.orm import Session
from tables import CycloneTrajectory
from pages.db import get_db_session 
import plotly.graph_objects as go

def register_callbacks(app):
    @app.callback(
        Output('cyclone-dropdown', 'options'),
        Input('season-slider', 'value')
    )
    def update_cyclone_dropdown(season):
        session: Session = get_db_session()
        names = session.query(CycloneTrajectory.name).filter_by(season=season).distinct().all()
        return [{'label': name[0], 'value': name[0]} for name in names]

    @app.callback(
        Output('cyclone-path-map', 'figure'),
        Input('cyclone-dropdown', 'value'),
        Input('season-slider', 'value')
    )
    def plot_single_cyclone(name, season):
        session = get_db_session()
        if not name:
            fig = go.Figure(go.Scattermapbox())
            fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=3, mapbox_center={"lat": 21.5, "lon": -79.5})
            return fig

        df = pd.read_sql(
            session.query(CycloneTrajectory)
                .filter_by(name=name, season=season)
                .statement, session.bind
        )
        fig = px.line_mapbox(df, lat='lat', lon='lon', hover_data=['iso_time', 'usa_status'],
                            color_discrete_sequence=['blue'], zoom=4, height=400)
        fig.update_layout(mapbox_style='open-street-map')
        return fig

    @app.callback(
        Output('cyclone-wind-pressure', 'figure'),
        Input('cyclone-dropdown', 'value'),
        Input('season-slider', 'value')
    )
    def wind_pressure_plot(name, season):
        session = get_db_session()
        if not name:
            return px.line()
        df = pd.read_sql(
            session.query(CycloneTrajectory)
                   .filter_by(name=name, season=season)
                   .statement, session.bind
        )
        fig = px.line(df, x='iso_time', y=['usa_wind', 'usa_pres'],
                      labels={'value': 'Intensidad', 'variable': 'Variable'})
        return fig
