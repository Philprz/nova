from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import os
import json
import requests
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
print(">>> API KEY:", os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI()
# Initialisation Salesforce
sf = Salesforce(
    username=os.getenv("SALESFORCE_USERNAME"),
    password=os.getenv("SALESFORCE_PASSWORD"),
    security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
    domain=os.getenv("SALESFORCE_DOMAIN", "login")
)
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

# WebSocket MCP
@app.websocket("/mcp")
async def mcp_endpoint(websocket: WebSocket):
    await websocket.accept()
    capabilities = {
        "server_info": {"name": "Custom MCP Server", "version": "1.0"},
        "tools": {
            "salesforce": {"description": "Salesforce access", "operations": ["query"]},
            "sap": {"description": "SAP access", "operations": ["read"]}
        }
    }
    await websocket.send_json({"type": "capabilities", "data": capabilities})

    try:
        while True:
            msg = await websocket.receive_text()
            request = json.loads(msg)
            response = await handle_mcp_request(request["data"])
            await websocket.send_json({"type": "response", "data": response})
    except Exception:
        await websocket.close()

async def handle_mcp_request(data):
    action = data.get("action")
    if action == "salesforce.query":
        return {"result": sf.query(data["parameters"]["query"])}
    elif action == "sap.read":
        return {"result": sap_read(data["parameters"])}
    return {"error": "Unknown action"}

def sap_read(params):
    # Placeholder : vous devrez implémenter la logique SAP avec pyrfc
    return {"table": params.get("table"), "criteria": params.get("criteria")}