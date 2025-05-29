import dash
from dash import dcc, html, Input, Output, State
import psycopg2
from pages.forecast.layout import forecast_layout
from pages.historical.layout import historical_analysis_layout
from pages.auth.layout import auth_layout
from pages.forecast.callbacks import register_callbacks as register_forecast_callbacks
from pages.historical.callbacks import register_callbacks as register_historical_callbacks
from pages.auth.login_callback import register_login_callbacks
from pages.auth.register_callback import register_register_callbacks
from pages.cyclones.callbacks import register_callbacks as register_cyclones_callbacks
from pages.cyclones.layout import cyclone_layout
from src.storage.config import DATABASE_URL

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Weather Dashboard"

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="session-role", data=None),
    html.Div(id="page-content")
])

def default_main_content():
    return html.Div([
        html.H1("Análisis y predicción del clima de Cuba"),
        html.P("Este dashboard ofrece información sobre la evolución del clima por más de 30 años. Tiene en cuenta varias variables meteorológicas, desde temperatura, viento, humedad, precipitaciones, rocío, entre otras."),
        html.P("Puede analizar registros históricos o consultar el pronóstico del clima para las próximas horas."),
        html.Img(src="/assets/clima.png", style={"width": "85%", "display": "block", "margin": "auto"})
    ])
def layout_with_sidebar(content, role):
    links = [
        dcc.Link("Análisis histórico del clima 📈", href="/historical_analysis"),
        html.Br(),
        dcc.Link("Pronóstico del tiempo ⛅", href="/forecast"),
    ]

    # Solo para usuarios logueados (no guests)
    if role in ("user", "admin"):
        links.extend([
            html.Br(),
            dcc.Link("Eventos meteorológicos 🌪️", href="/cyclones")
        ])

    return html.Div([
        html.Div([
            html.H2("Menú principal"),
            *links
        ], className="sidebar"),
        html.Div(content, className="content")
    ])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    State("session-role", "data")
)
def display_page(pathname, role):
    if role is None:
        return auth_layout
    if pathname == "/forecast":
        return layout_with_sidebar(forecast_layout, role)
    elif pathname == "/historical_analysis":
        return layout_with_sidebar(historical_analysis_layout, role)
    elif pathname == "/cyclones":
        return layout_with_sidebar(cyclone_layout, role)
    else:
        return layout_with_sidebar(default_main_content(), role)

register_forecast_callbacks(app)
register_historical_callbacks(app)
register_login_callbacks(app)
register_register_callbacks(app)
register_cyclones_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)