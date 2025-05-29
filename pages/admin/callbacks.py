from dash import Input, Output, dcc, html
import plotly.express as px
import pandas as pd
from sqlalchemy.orm import Session
from pages.db import get_db_session
from datetime import datetime, timedelta
from src.storage.tables import UserInteraction, Ubicacion
import dash

def register_callbacks(app):
    @app.callback(
        Output("page-visit-graph", "figure"),
        Output("historical-interactions-graph", "figure"),
        Output("forecast-interactions-graph", "figure"),
        Output("cyclones-interactions-graph", "figure"),
        Output("interaction-table", "data"),
        Input("url", "pathname")
    )
    def update_admin_data(pathname):
        if pathname != "/admin_page": 
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
        session = get_db_session()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Visitas por pagina
        page_counts = session.query(UserInteraction.page).filter(UserInteraction.timestamp >= thirty_days_ago).all()
        df_pages = pd.DataFrame(page_counts, columns=["Página"])
        fig_pages = px.histogram(df_pages, x="Página", title="Visitas por Página en los últimos 30 días")

        # Contadores dentro de cada página
        historical_interactions = session.query(UserInteraction.component_id).filter(
            UserInteraction.page == "historical", UserInteraction.timestamp >= thirty_days_ago).all()
        df_hist = pd.DataFrame(historical_interactions, columns=["Componente"])
        fig_hist = px.histogram(df_hist, x="Componente", title="Interacciones en Historical")

        forecast_interactions = session.query(UserInteraction.component_id).filter(
            UserInteraction.page == "forecast", UserInteraction.timestamp >= thirty_days_ago).all()
        df_forecast = pd.DataFrame(forecast_interactions, columns=["Componente"])
        fig_forecast = px.histogram(df_forecast, x="Componente", title="Interacciones en Forecast")

        cyclones_interactions = session.query(UserInteraction.component_id).filter(
            UserInteraction.page == "cyclones", UserInteraction.timestamp >= thirty_days_ago).all()
        df_cyclones = pd.DataFrame(cyclones_interactions, columns=["Componente"])
        fig_cyclones = px.histogram(df_cyclones, x="Componente", title="Interacciones en Cyclones")

        # interacciones en los últimos 30 días
        all_interactions = session.query(UserInteraction.page, UserInteraction.component_id, UserInteraction.value, UserInteraction.timestamp).filter(
            UserInteraction.timestamp >= thirty_days_ago).all()
        df_table = pd.DataFrame(all_interactions, columns=["Página", "Componente", "Valor", "Fecha"])
        

        session.close()

        return fig_pages, fig_hist, fig_forecast, fig_cyclones, df_table.to_dict("records")
