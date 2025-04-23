from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Middleware LLM opérationnel"}

@app.get("/api-key")
def show_api_key():
    return {"key": os.getenv("ANTHROPIC_API_KEY", "non définie")}
