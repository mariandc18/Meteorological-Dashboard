from dash import html, dcc

register_layout = html.Div([
    html.Div([
        html.H3("Registro de nuevo usuario"),
        dcc.Input(id="register-username", placeholder="Nombre de usuario", type="text", style={"marginBottom": "10px", "width": "100%"}),
        dcc.Input(id="register-password", placeholder="Contraseña", type="password", style={"marginBottom": "10px", "width": "100%"}),
        dcc.Input(id="register-password-confirm", placeholder="Confirmar contraseña", type="password", style={"marginBottom": "10px", "width": "100%"}),
        html.Button("Registrarse", id="register-button", style={"width": "100%"}),
        html.Div(id="register-message", style={"color": "red", "marginTop": "10px"}),

        html.Hr(),

        html.Div([
            html.P("¿Ya tienes cuenta?"),
            dcc.Link("Volver al inicio de sesión", href="/login"),
        ], style={"marginTop": "10px"})
    ], style={
        "maxWidth": "400px",
        "margin": "auto",
        "textAlign": "center",
        "padding": "50px",
        "border": "1px solid #ccc",
        "borderRadius": "10px",
        "backgroundColor": "#f9f9f9"
    })
])