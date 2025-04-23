from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

app = FastAPI()

class MessageRequest(BaseModel):
    prompt: str

@app.get("/")
def hello():
    return {"message": "Middleware LLM opérationnel"}

@app.post("/claude")
def ask_claude(request: MessageRequest):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 512,
        "messages": [
            {"role": "user", "content": request.prompt}
        ]
    }

    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
    return response.json()

