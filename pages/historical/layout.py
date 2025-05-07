from dash import dcc, html

historical_analysis_layout = html.Div([
    html.H3("Análisis histórico del clima"),
    html.Div([
        dcc.Dropdown(
            id="data-type",
            options=[
                {"label": "Hourly", "value": "hourly"},
                {"label": "Daily", "value": "daily"}
            ],
            value="hourly"
        ),
        dcc.Dropdown(
            id="provincia",
            options=[],
            placeholder="Provincia"
        ),
        dcc.Dropdown(
            id="municipio",
            options=[],
            placeholder="Municipio"
        ),
        dcc.Dropdown(
            id="variable",
            options=[],
            placeholder="Variable"
        ),
    ], style={"marginBottom": "20px"}),
    dcc.DatePickerRange(
        id="date-picker-range",
        start_date_placeholder_text="Inicio",
        end_date_placeholder_text="Fin"
    ),
    dcc.RadioItems(
        id="agregacion",
        options=[
            {"label": "Diario", "value": "day"},
            {"label": "Mensual", "value": "month"},
            {"label": "Anual", "value": "year"}
        ],
        value="day",
        labelStyle={"display": "inline-block", "marginRight": "10px"}
    ),
    dcc.Graph(id="weather-graph")
])