from dash import Input, Output, State, dcc
from flask import make_response
from auth.authentication_manager import AuthManager
from auth.session import set_uid_cookie
from dash.exceptions import PreventUpdate
import dash

auth_manager = AuthManager()

def register_login_callbacks(app):
    @app.callback(
        Output("login-message", "children"),
        Output("session-role", "data"),  
        Output("url", "pathname"),                
        Input("login-button", "n_clicks"),
        State("login-username", "value"),
        State("login-password", "value"),
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password):
        if not username or not password:
            return "Por favor, complete todos los campos.", None, "/login"
       
        user = auth_manager.login_user(username, password)
        if user:
            response = make_response("OK")
            set_uid_cookie(response, str(user.cookie_uid))

            path = "/admin_page" if user.role == "admin" else "/home"
            return "", user.role, path
        else:
            return "Credenciales inválidas.", None, "/login"
