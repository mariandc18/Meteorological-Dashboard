import requests
import json
import os

def load_prompt(file_path):
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

def call_llm_classification(prompt: str, model = "mistral"):
    response = requests.post("http://localhost:11434/api/generate", json={"model": model, "prompt": prompt, "stream": False})
    return response.json()["response"].strip()

def analyze_user_prompt(user_prompt: str) -> dict:
    prompt_template = load_prompt("./prompts/user_prompt.txt")

    full_prompt = f"{prompt_template}\n\nUsuario:\n{user_prompt}"
    raw_response = call_llm_classification(full_prompt)

    try:
        data = json.loads(raw_response)
        return {
            "related_to_weather": data.get("related_to_weather", False),
            "location": data.get("location")
        }
    except json.JSONDecodeError:
        print("Error al interpretar la respuesta del modelo:", raw_response)
        return {"related_to_weather": False, "location": None}
