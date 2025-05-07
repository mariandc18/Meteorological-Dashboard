from dash import dcc, html

forecast_layout = html.Div([
    html.H3("Pronóstico del Tiempo"),
    html.Div([
        dcc.Dropdown(
            id="forecast-provincia",
            options=[],  # Se actualiza automáticamente
            placeholder="Selecciona la provincia",
            style={"width": "30%", "display": "inline-block"}
        ),
        dcc.Dropdown(
            id="forecast-municipio",
            options=[],  # Se actualizará en función de la provincia seleccionada
            placeholder="Selecciona el municipio"
        ),
    ]),
    html.Div(id="forecast-graphs")  # Aquí se cargarán los gráficos de pronóstico
])