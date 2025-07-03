from dash import html, dcc
from dash.dash_table import DataTable

layout = html.Div([
    html.H2("Historial de Interacciones", className="header"),
    
    dcc.Store(id="historial-interactions-store"),

    html.Div([
        DataTable(
            id="tabla-historial",
            columns=[
                {"name": "Página", "id": "page"},
                {"name": "Componente", "id": "component_id"},
                {"name": "Valor", "id": "value"},
                {"name": "Fecha", "id": "timestamp"},
                {"name": "Eliminar", "id": "delete", "presentation": "markdown"}
            ],
            data=[],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
        )
    ], className="card"),  
    
    html.Div(id="feedback-eliminar", className="feedback-msg")
], className="main-container")