from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from sqlalchemy.orm import Session
from src.storage.tables import User, SavedView
from pages.db import get_db_session
import dash
import json

def register_callbacks(app: dash.Dash):
    @app.callback(
        Output("tabla-historial", "data"),
        Input("url", "pathname"),
        Input("user-session", "data"),
    )
    def load_saved_views(pathname, user_data):
        if pathname != "/historial" or not user_data:
            raise PreventUpdate

        username = (
            user_data if isinstance(user_data, str)
            else user_data.get("username") if isinstance(user_data, dict)
            else None
        )
        if not username:
            raise PreventUpdate

        session: Session = get_db_session()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return []

        vistas = (
            session.query(SavedView)
            .filter_by(user_id=user.id)
            .order_by(SavedView.timestamp.desc())
            .all()
        )

        data = [
            {
                "id": str(v.id),
                "name": v.name,
                "page": v.page,
                "timestamp": v.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "go": "[🔁](go)",
                "delete": "[❌](delete)"
            }
            for v in vistas
        ]
        return data

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("url", "search", allow_duplicate=True),
        Input("tabla-historial", "active_cell"),
        State("tabla-historial", "data"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def navegar_a_vista_guardada(active_cell, tabla_data, user_data):
        if not active_cell or active_cell["column_id"] != "go":
            raise PreventUpdate

        fila = active_cell["row"]
        vista = tabla_data[fila]

        username = (
            user_data if isinstance(user_data, str)
            else user_data.get("username") if isinstance(user_data, dict)
            else None
        )
        if not username:
            raise PreventUpdate

        session: Session = get_db_session()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            raise PreventUpdate

        vista_guardada = session.query(SavedView).filter_by(id=vista["id"], user_id=user.id).first()
        if not vista_guardada:
            raise PreventUpdate

        try:
            params = json.loads(vista_guardada.params)
        except Exception:
            params = {}

        query_string = "?" + "&".join(
            f"{k}={','.join(map(str, v)) if isinstance(v, list) else v}"
            for k, v in params.items()
        )

        print("DEBUG destino:", vista_guardada.page)
        print("DEBUG query:", query_string)
        return ("/" + vista_guardada.page.lstrip("/")), query_string