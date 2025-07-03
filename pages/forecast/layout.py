from dash import dcc, html

forecast_layout = html.Div([
    html.H3("Pronóstico del Tiempo", className="forecast-title"),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id="forecast-provincia",
                options=[],
                placeholder="Selecciona la provincia",
                className="weather-dropdown forecast-dropdown"
            ),
            dcc.Dropdown(
                id="forecast-municipio",
                options=[],
                placeholder="Selecciona el municipio",
                className="weather-dropdown forecast-dropdown"
            ),
        ], className="forecast-selectors"),
        
        html.Div(id="forecast-graphs", className="forecast-graphs-container")
    ], className="forecast-main")
], className="main-container")