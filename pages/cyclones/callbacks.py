from dash import Input, Output, html, dcc
import plotly.express as px
import pandas as pd
from sqlalchemy.orm import Session
from src.storage.tables import CycloneTrajectory, UserInteraction
from pages.db import get_db_session  
import plotly.graph_objects as go
from datetime import datetime
import uuid
from pages.tracking import log_interaction_by_username

def register_callbacks(app):
    @app.callback(
        Output('cyclone-dropdown', 'options'),
        [Input('season-slider', 'value'), Input('user-session', 'data')]
    )
    def update_cyclone_dropdown(season_range, user_data):
        start_year, end_year = season_range
        session: Session = get_db_session()
        names = (
            session.query(CycloneTrajectory.name)
            .filter(CycloneTrajectory.season >= start_year, CycloneTrajectory.season <= end_year)
            .distinct()
            .all()
        )

        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "cyclones", "season-slider", f"Rango {start_year}-{end_year}")

        return [{'label': name[0], 'value': name[0]} for name in names]

    @app.callback(
        Output('cyclone-path-map', 'figure'),
        [Input('cyclone-dropdown', 'value'), Input('season-slider', 'value'), Input('user-session', 'data')]
    )
    def plot_single_cyclone(name, season_range, user_data):
        session = get_db_session()
        if not name:
            fig = go.Figure(go.Scattermapbox())
            fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=3, mapbox_center={"lat": 21.5, "lon": -79.5})
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            return fig

        start_year, end_year = season_range
        df = pd.read_sql(
            session.query(CycloneTrajectory)
                .filter(
                    CycloneTrajectory.name == name,
                    CycloneTrajectory.season.between(start_year, end_year)
                )
                .order_by(CycloneTrajectory.iso_time)
                .statement,
            session.bind
        )

        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "cyclones", "cyclone-dropdown", name)
        
        fig = px.line_mapbox(df, lat='lat', lon='lon', hover_data=['iso_time', 'usa_status'],
                            color_discrete_sequence=['blue'], zoom=4, height=400)
        fig.update_layout(mapbox_style='open-street-map')
        return fig

    @app.callback(
        Output('graph-sshs', 'figure'),
        Output('graph-dist2land', 'figure'),
        Output('graph-landfall', 'figure'),
        [Input('cyclone-dropdown', 'value'), Input('season-slider', 'value'), Input('user-session', 'data')]
    )
    def cyclone_details_plot(name, season_range, user_data):
        session = get_db_session()

        if not name or not season_range:
            empty_fig = px.line()
            return empty_fig, empty_fig, empty_fig

        start_year, end_year = season_range
        query = (
            session.query(CycloneTrajectory)
            .filter(
                CycloneTrajectory.name == name,
                CycloneTrajectory.season.between(start_year, end_year)
            )
            .order_by(CycloneTrajectory.iso_time)
        )

        df = pd.read_sql(query.statement, session.bind)
        
        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "cyclones", "cyclone-details", name)

        fig_sshs = px.line(df, x='iso_time', y='usa_sshs',
                        title='Categoría SSHS',
                        labels={'iso_time': 'Fecha', 'usa_sshs': 'Categoría Saffir-Simpson'})

        fig_dist2land = px.line(df, x='iso_time', y='dist2land',
                                title='Distancia a Tierra',
                                labels={'iso_time': 'Fecha', 'dist2land': 'Distancia (km)'})

        fig_landfall = px.line(df, x='iso_time', y='landfall',
                            title='Landfall (1 = sí)',
                            labels={'iso_time': 'Fecha', 'landfall': 'Landfall'})

        return fig_sshs, fig_dist2land, fig_landfall

    @app.callback(
        Output('all-cyclones-paths', 'figure'),
        Output('wind-comparison', 'figure'),
        Output('pressure-comparison', 'figure'),
        [Input('season-slider', 'value'), Input('user-session', 'data')]
    )
    def compare_cyclones(season_range, user_data):
        start_year, end_year = season_range
        session = get_db_session()
        df = pd.read_sql(
            session.query(CycloneTrajectory)
            .filter(CycloneTrajectory.season >= start_year, CycloneTrajectory.season <= end_year)
            .statement,
            session.bind
        )
        df['step'] = df.groupby('name').cumcount()
        username = user_data if isinstance(user_data, str) else None
        log_interaction_by_username(username, "cyclones", "all-cyclones-paths", f"Comparación temporada {start_year}-{end_year}")
        
        fig_paths = px.line_mapbox(df, lat='lat', lon='lon', color='name', hover_data=['step'],
                                   zoom=3, height=400)
        fig_paths.update_layout(mapbox_style='open-street-map')

        wind_fig = px.line(df, x='step', y='usa_wind', color='name', title='Comparación de Viento')
        pres_fig = px.line(df, x='step', y='usa_pres', color='name', title='Comparación de Presión')

        return fig_paths, wind_fig, pres_fig