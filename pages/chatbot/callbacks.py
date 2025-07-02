from dash import Input, Output, State, callback
from src.chatbot.providers.openmeteo import OpenMeteoProvider
from src.chatbot.providers.visual_crossing import VisualCrossingProvider
from src.chatbot.middleware import ForecastAggregator, AggregatedForecast
from src.chatbot.models.forecast import Location
from src.chatbot.response_generator import generate_forecast_response
from src.chatbot.prompt_analyzer import analyze_user_prompt
from src.chatbot.cache.cache_manager import get_forecast, save_forecast
from datetime import date, timedelta
from pages.tracking import log_interaction

def register_callbacks(app):
    
    @app.callback(
        Output("chatbot-response-output", "children"),
        Input("send-button", "n_clicks"),
        State("chat-input", "value"),
        State("user-session", "data")
    )
    def handle_user_question(n_clicks, user_prompt, user_data):
        if not user_prompt:
            return "Escribe algo para poder ayudarte."

        analysis = analyze_user_prompt(user_prompt)
        if not analysis["related_to_weather"]:
            return "Lo siento, solo puedo responder preguntas relacionadas con el clima."
        if not analysis["location"]:
            return "Por favor, dime a qué ciudad o región te refieres."

        location_name = analysis["location"]
        location = Location(name=location_name, lat=None, lon=None)
        
        user_id = user_data.get("user_id") if user_data else None
        log_interaction(user_id, "chatbot", "chatbot-response-output", f"Consultó clima para {location_name}")

        cached = get_forecast(location_name)
        if cached:
            print(f"Caché encontrada para {location_name}")
            aggregated = [
                AggregatedForecast(merged=f, by_source={})
                for f in cached
            ]
        else:
            print(f"No hay caché, consultando APIs para {location_name}")
            providers = [
                VisualCrossingProvider(api_key="api_key"),
                OpenMeteoProvider()
            ]
            aggregator = ForecastAggregator(providers=providers)
            range = (date.today(), date.today() + timedelta(days=7))
            aggregated = aggregator.aggregate_daily_forecasts(location, range)

            merged_data = [day.merged for day in aggregated]
            save_forecast(location_name, merged_data)
              
        return generate_forecast_response(location, None, user_prompt=user_prompt, precomputed=aggregated)
