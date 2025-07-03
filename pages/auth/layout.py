from dash import html, dcc

auth_layout = html.Div([

    html.Div([
        html.H4("Iniciar Sesión"),
        dcc.Input(id="login-username", type="text", placeholder="Usuario", debounce=True, className="login-input"),
        dcc.Input(id="login-password", type="password", placeholder="Contraseña", debounce=True, className="login-input"),
        html.Button("Iniciar Sesión", id="login-button", className="login-button"),
        html.Div(id="login-message", className="login-message"),
        html.Hr(),
        html.H4("¿Nuevo aquí? Regístrate"),
        dcc.Input(id="register-username", type="text", placeholder="Nuevo usuario", debounce=True, className="login-input"),
        dcc.Input(id="register-password", type="password", placeholder="Contraseña", debounce=True, className="login-input"),
        dcc.Input(id="register-password-confirm", type="password", placeholder="Confirmar contraseña", debounce=True, className="login-input"),
        html.Button("Registrarse", id="register-button", className="login-button"),
        html.Div(id="register-message", className="login-message"),
        html.Hr()
    ], className="login-container" ) 
], className="login-page")
