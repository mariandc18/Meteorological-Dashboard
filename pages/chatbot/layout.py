from dash import html, dcc

chatbot_layout = html.Div([
    #dcc.Store(id="user-session", storage_type="session"), 
    html.H2("Quieres saber cómo está el clima hoy en alguna parte del mundo?", className="forecast-title"),

    html.Div([
        dcc.Textarea(
            id="chat-input",
            placeholder="Pregúntame sobre el clima en cualquier ciudad…",
            className="chatbot-input",
            rows=3
        ),
        html.Button("Enviar", id="send-button", className="button", n_clicks=0)
    ], className="chatbot-controls"),

    html.Div(id="chatbot-response-output", className="chatbot-output card")
], className="forecast-main")