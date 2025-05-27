from dash import html, dcc

login_layout = html.Div([
    html.Div([
        html.H3("Iniciar sesión"),
        dcc.Input(id="login-username", placeholder="Usuario", type="text"),
        dcc.Input(id="login-password", placeholder="Contraseña", type="password"),
        html.Button("Iniciar sesión", id="login-button"),
        html.Div(id="login-message", style={"color": "red", "marginTop": "10px"}),

        html.Hr(),

        html.Div([
            html.P("¿No tienes cuenta?"),
            dcc.Link("Registrarse", href="/register"),
        ]),
        html.Br(),
        html.Div([
            html.P("O puedes continuar como invitado:"),
            dcc.Link("Entrar como invitado", href="/guest"),
        ])
    ], style={"maxWidth": "400px", "margin": "auto", "textAlign": "center", "padding": "50px"})
])