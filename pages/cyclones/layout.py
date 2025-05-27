from dash import dcc, html

cyclone_layout = html.Div([
    html.H2("Análisis de Ciclones que han pasado por Cuba"),

    html.Label("Selecciona una temporada:"),
    dcc.Slider(
        id='season-slider',
        min=2000,
        max=2025,
        step=1,
        value=2000,
        marks={i: str(i) for i in range(2000, 2026, 5)},
        tooltip={"placement": "bottom", "always_visible": False}
    ),

    html.Br(),
    html.Label("Selecciona un ciclón:"),
    dcc.Dropdown(id='cyclone-dropdown', placeholder='Selecciona un ciclón', multi=False),

    html.Hr(),
    html.H3("Trayectoria del ciclón seleccionado"),
    dcc.Graph(id='cyclone-path-map'),

    html.H3("Evolución del viento y presión del ciclón"),
    dcc.Graph(id='cyclone-wind-pressure'),

    html.Hr(),
    html.H3("Comparación de todos los ciclones en la temporada"),
    dcc.Graph(id='all-cyclones-paths'),
    dcc.Graph(id='wind-comparison'),
    dcc.Graph(id='pressure-comparison')
])