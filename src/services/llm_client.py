import requests
from src.config import OPENROUTER_API_KEY, MODEL_NAME

def ask_openrouter(messages):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "X-Title": "FastAPI Chat",
        },
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "max_tokens": 512,
        }
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]
