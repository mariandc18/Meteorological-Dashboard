from dash import Input, Output, State, callback
from src.chatbot.providers.openmeteo import OpenMeteoProvider
from src.chatbot.providers.visual_crossing import VisualCrossingProvider
from src.chatbot.middleware import ForecastAggregator
from src.chatbot.models.forecast import Location
from src.chatbot.response_generator import generate_forecast_response
from src.chatbot.prompt_analyzer import analyze_user_prompt

def register_callbacks(app):

    @app.callback(
        Output("chatbot-response-output", "children"),
        Input("send-button", "n_clicks"),
        State("chat-input", "value")
    )
    def handle_user_question(n_clicks, user_prompt):
        if not user_prompt:
            return "Escribe algo para poder ayudarte."
        
        analysis = analyze_user_prompt(user_prompt)
        if not analysis["related_to_weather"]:
            return "Lo siento, solo puedo responder preguntas relacionadas con el clima."

        if not analysis["location"]:
            return "Por favor, dime a qué ciudad o región te refieres."

        providers = [
            VisualCrossingProvider(api_key="api_key"),
            OpenMeteoProvider()
        ]
        location = Location(name=analysis["location"], lat=None, lon=None)
        aggregator = ForecastAggregator(providers=providers)

        return generate_forecast_response(location, aggregator, user_prompt=user_prompt)
