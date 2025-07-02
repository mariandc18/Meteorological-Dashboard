import json
from src.chatbot.middleware import ForecastAggregator, AggregatedForecast
from src.chatbot.models.forecast import Location
from datetime import timedelta, date
import requests
import numpy as np
import os

def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def custom_json_encoder(obj):
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def generate_llm_input(location, aggregated):
    return ForecastAggregator([]).prepare_llm_input(location, aggregated)

def assemble_prompt(prompt_text, llm_input):
    context_str = json.dumps(llm_input, indent=2, ensure_ascii=False, default=custom_json_encoder)
    return f"{prompt_text}\n\nContexto:\n{context_str}"

def call_llm(prompt, model= "mistral"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["response"].strip()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return "Hubo un error al conectarse con el modelo"

def generate_forecast_response(location, aggregator, user_prompt, precomputed=None):
    if precomputed:
        aggregated = precomputed
    else:
        range = (date.today(), date.today() + timedelta(days=7))
        aggregated = aggregator.aggregate_daily_forecasts(location, range)

    llm_input = generate_llm_input(location.name, aggregated)
    llm_input["user_prompt"] = user_prompt  

    BASE_DIR = os.path.dirname(__file__)
    prompt_path = os.path.join(BASE_DIR, "./prompts/prompt.txt")
    prompt_template = load_prompt(prompt_path)

    full_prompt = assemble_prompt(prompt_template, llm_input)
    response = call_llm(full_prompt)
    return response
