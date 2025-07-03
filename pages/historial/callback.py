from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from sqlalchemy.orm import Session
from src.storage.tables import User, UserInteraction
from pages.db import get_db_session
import dash

def register_callbacks(app: dash.Dash):

    @app.callback(
        Output("tabla-historial", "data"),
        Input("user-session", "data"),
    )
    def load_history(user_data):
        if not user_data:
            raise PreventUpdate
        
        username = user_data 
        session: Session = get_db_session()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return []

        interactions = (
            session.query(UserInteraction)
            .filter_by(user_id=user.id, deleted=False)
            .order_by(UserInteraction.timestamp.desc())
            .all()
        )

        data = [
            {
                "id": str(inter.id),
                "page": inter.page,
                "component_id": inter.component_id,
                "value": inter.value,
                "timestamp": inter.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "delete": "[❌](delete)"
            }
            for inter in interactions
        ]
        return data

    @app.callback(
        Output("feedback-eliminar", "children"),
        Output("tabla-historial", "data", allow_duplicate=True),
        Input("tabla-historial", "active_cell"),
        State("tabla-historial", "data"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def delete_interaction(active_cell, data, user_data):
        if not active_cell or active_cell["column_id"] != "delete":
            raise PreventUpdate

        row_index = active_cell["row"]
        interaction_id = data[row_index]["id"]

        username = user_data  
        session: Session = get_db_session()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return "Usuario no encontrado.", data

        interaction = session.query(UserInteraction).filter_by(id=interaction_id, user_id=user.id).first()
        if not interaction:
            return "Interacción no encontrada.", data

        interaction.deleted = True
        session.commit()

        interactions = (
            session.query(UserInteraction)
            .filter_by(user_id=user.id, deleted=False)
            .order_by(UserInteraction.timestamp.desc())
            .all()
        )
        updated_data = [
            {
                "id": str(inter.id),
                "page": inter.page,
                "component_id": inter.component_id,
                "value": inter.value,
                "timestamp": inter.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "delete": "[❌](delete)"
            }
            for inter in interactions
        ]
        return "Interacción eliminada correctamente.", updated_data