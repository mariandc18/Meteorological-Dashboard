from dash import dcc, html
import dash.dash_table as dash_table

admin_layout = html.Div([
    html.H1("Panel de Administración📝", style={"textAlign": "center", "marginBottom": "20px"}),
    
    html.Div([
        html.H2("Visitas por Página"),
        html.P("Cantidad de accesos a cada página en los últimos 30 días."),
        dcc.Graph(id="page-visit-graph"),
    ], style={"marginBottom": "40px"}),

    html.Div([
        html.H2("Interacciones dentro de cada página"),
        html.P("Frecuencia con la que los usuarios han usado botones, dropdowns y otros componentes."),
        
        html.H3("Interacciones en Análisis Históricos"),
        dcc.Graph(id="historical-interactions-graph"),
        
        html.H3("Interacciones en Forecast"),
        dcc.Graph(id="forecast-interactions-graph"),
        
        html.H3("Interacciones en Cyclones"),
        dcc.Graph(id="cyclones-interactions-graph"),
    ], style={"marginBottom": "40px"}),
    
    html.Div([
    html.H2("Ubicaciones más consultadas"),
    dash_table.DataTable(
        id="most-consulted-table",
        columns=[
            {"name": "Provincia", "id": "Provincia"},
            {"name": "Municipio", "id": "Municipio"},
            {"name": "Frecuencia", "id": "Frecuencia"},
        ],
        page_size=10
    )
]),
    html.Div([
        html.H2("Detalles de interacciones"),
        html.P("Tabla con todas las acciones registradas en los últimos 30 días."),
        dash_table.DataTable(id="interaction-table", page_size=10)
    ], style={"marginBottom": "40px"})
])
