from dash import Input, Output, State, dcc
from auth.authentication_manager import AuthManager
from dash.exceptions import PreventUpdate
from flask import make_response
from auth.session import set_uid_cookie
import uuid

auth_manager = AuthManager()

def register_register_callbacks(app):
    @app.callback(
        Output("register-message", "children"),
        Input("register-button", "n_clicks"),
        State("register-username", "value"),
        State("register-password", "value"),
        State("register-password-confirm", "value"),
        prevent_initial_call=True
    )
    def handle_register(n_clicks, username, password, confirm_password):
        if not username or not password or not confirm_password:
            return "Todos los campos son obligatorios."

        if password != confirm_password:
            return "Las contraseñas no coinciden."

        try:
            user = auth_manager.register_user(username, password)
            return "Registro exitoso."
        except Exception as e:
            return f"Error al registrar usuario: {str(e)}"

def register_guest_callbacks(app):
    @app.callback(
        Output("login-message", "children"),
        Input("guest-button", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_guest(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        uid = str(uuid.uuid4()) 
        response = make_response()
        set_uid_cookie(response, uid)
        return dcc.Location(href="/", id="redirect-guest")