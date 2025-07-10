from dash import dcc, html

historical_analysis_layout = html.Div([
    html.H3("Análisis histórico del clima ⛅", className="weather-title"),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id="data-type",
                options=[
                    {"label": "Hourly", "value": "hourly"},
                    {"label": "Daily", "value": "daily"}
                ],
                value="hourly",
                className="weather-dropdown"
            ),
            dcc.Dropdown(
                id="provincia",
                options=[],
                placeholder="Provincia",
                className="weather-dropdown"
            ),
            dcc.Dropdown(
                id="municipio",
                options=[],
                placeholder="Municipio",
                className="weather-dropdown"
            ),
            dcc.Dropdown(
                id="variable",
                options=[],
                placeholder="Variable",
                className="weather-dropdown"
            ),
        ], className="dropdown-grid"),
        
        html.Div([
            dcc.DatePickerRange(
                id="date-picker-range",
                start_date_placeholder_text="Inicio",
                end_date_placeholder_text="Fin",
                className="weather-datepicker"
            ),
        ], className="datepicker-container"),
        
        dcc.RadioItems(
            id="agregacion",
            options=[
                {"label": "Diario", "value": "day"},
                {"label": "Mensual", "value": "month"},
                {"label": "Anual", "value": "year"}
            ],
            value="day",
            className="weather-radio",
            labelClassName="weather-radio-label"
        ),
    ], className="controls-container"),
    
    html.Div([
        html.Label("Nombre para guardar esta vista:"),
        dcc.Input(id="nombre-vista-historical", placeholder="Ej: Santiago - Precipitación", type="text"),
        html.Button("Guardar vista", id="guardar-vista-btn-historical", n_clicks=0),
        html.Div(id="feedback-guardar-vista-historical")
    ], style={"margin": "20px 0"}),

    dcc.Graph(id="weather-graph", className="weather-graph")
], className="main-container")