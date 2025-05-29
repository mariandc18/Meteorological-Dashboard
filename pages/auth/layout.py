from dash import html, dcc

auth_layout = html.Div([
    html.H2("Weather Dashboard 🌦️"),
    html.Div([
        html.H4("Iniciar Sesión"),
        dcc.Input(id="login-username", type="text", placeholder="Usuario", debounce=True),
        dcc.Input(id="login-password", type="password", placeholder="Contraseña", debounce=True),
        html.Button("Iniciar Sesión", id="login-button"),
        html.Div(id="login-message", style={"color": "red", "marginTop": "10px"}),
        html.Hr(),
        html.H4("¿Nuevo aquí? Regístrate"),
        dcc.Input(id="register-username", type="text", placeholder="Nuevo usuario", debounce=True),
        dcc.Input(id="register-password", type="password", placeholder="Contraseña", debounce=True),
        dcc.Input(id="register-password-confirm", type="password", placeholder="Confirmar contraseña", debounce=True),
        html.Button("Registrarse", id="register-button"),
        html.Div(id="register-message", style={"color": "green", "marginTop": "10px"}),
        html.Hr()], style={"maxWidth": "400px", "margin": "auto"})
])
